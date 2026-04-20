use anyhow::{Result, anyhow, bail};
use postgresql_archive::{ExactVersion, Version, get_version};
use postgresql_embedded::{LATEST, PostgreSQL, Settings, SettingsBuilder};
use serde::Serialize;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

const MANAGED_TIMEOUT_SECS: u64 = 30;

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct ToolBinaryStatus {
    pub path: Option<PathBuf>,
    pub present: bool,
    pub executable: bool,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct HostToolingStatus {
    pub configured_dir: Option<PathBuf>,
    pub valid: bool,
    pub pg_dump: ToolBinaryStatus,
    pub pg_restore: ToolBinaryStatus,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct ManagedToolingStatus {
    pub root: Option<PathBuf>,
    pub version_requirement: String,
    pub expected_version: Option<String>,
    pub binary_dir: Option<PathBuf>,
    pub matching_installed_version: Option<String>,
    pub stale_installed_versions: Vec<String>,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct ToolingStatus {
    pub active_backend: String,
    pub host: HostToolingStatus,
    pub managed: ManagedToolingStatus,
    pub would_download: bool,
}

#[derive(Debug, Clone)]
pub struct ToolBackend {
    binary_dir: PathBuf,
}

impl ToolBackend {
    pub fn binary_dir(&self) -> PathBuf {
        self.binary_dir.clone()
    }
}

pub async fn tooling_status() -> Result<ToolingStatus> {
    let host = inspect_host_status();
    validate_explicit_host(&host)?;

    let managed = inspect_managed_status().await?;
    Ok(build_tooling_status(host, managed))
}

pub async fn install_managed_tools() -> Result<ToolingStatus> {
    let host = inspect_host_status();
    if host.configured_dir.is_some() {
        validate_explicit_host(&host)?;
        bail!(
            "`tools install` manages the embedded PostgreSQL cache only. Unset DB_PG_BIN_DIR to provision managed tools."
        );
    }

    let managed_root = resolve_managed_root()?.ok_or_else(|| {
        anyhow!("Failed to resolve a default cache directory for managed PostgreSQL tools.")
    })?;
    let managed = inspect_managed_status_for_root(managed_root.clone()).await?;
    maybe_announce_managed_download(&managed);
    provision_managed_root(&managed_root.root).await?;
    tooling_status().await
}

pub async fn ensure_backend() -> Result<ToolBackend> {
    let host = inspect_host_status();
    validate_explicit_host(&host)?;
    if host.valid {
        return Ok(ToolBackend {
            binary_dir: host.configured_dir.clone().expect("validated host dir"),
        });
    }

    let managed_root = resolve_managed_root()?.ok_or_else(|| {
        anyhow!("Failed to resolve a default cache directory for managed PostgreSQL tools.")
    })?;
    let managed = inspect_managed_status_for_root(managed_root.clone()).await?;
    if let Some(error) = &managed.error {
        bail!("{error}");
    }
    maybe_announce_managed_download(&managed);
    let binary_dir = provision_managed_root(&managed_root.root).await?;
    Ok(ToolBackend { binary_dir })
}

#[derive(Debug, Clone)]
struct ManagedRoot {
    root: PathBuf,
}

fn default_managed_root(cache_base_dir: PathBuf) -> PathBuf {
    cache_base_dir
        .join("dotagents")
        .join("skills")
        .join("postgres")
        .join("postgresql")
}

fn resolve_managed_root() -> Result<Option<ManagedRoot>> {
    if let Some(root) = env::var_os("DB_MANAGED_PG_DIR").map(PathBuf::from) {
        return Ok(Some(ManagedRoot { root }));
    }

    let Some(cache_base_dir) = default_cache_base_dir() else {
        return Ok(None);
    };
    Ok(Some(ManagedRoot {
        root: default_managed_root(cache_base_dir),
    }))
}

#[cfg(unix)]
fn default_cache_base_dir() -> Option<PathBuf> {
    if let Some(path) = env::var_os("XDG_CACHE_HOME").filter(|value| !value.is_empty()) {
        return Some(PathBuf::from(path));
    }

    env::var_os("HOME")
        .filter(|value| !value.is_empty())
        .map(PathBuf::from)
        .map(|home| home.join(".cache"))
}

#[cfg(not(unix))]
fn default_cache_base_dir() -> Option<PathBuf> {
    dirs::cache_dir()
}

fn managed_settings(install_root: &Path) -> Settings {
    SettingsBuilder::new()
        .installation_dir(install_root.to_path_buf())
        .version(LATEST.clone())
        .temporary(true)
        .timeout(Some(std::time::Duration::from_secs(MANAGED_TIMEOUT_SECS)))
        .build()
}

async fn inspect_managed_status() -> Result<ManagedToolingStatus> {
    let Some(managed_root) = resolve_managed_root()? else {
        return Ok(ManagedToolingStatus {
            root: None,
            version_requirement: LATEST.to_string(),
            expected_version: None,
            binary_dir: None,
            matching_installed_version: None,
            stale_installed_versions: vec![],
            error: Some(
                "Failed to resolve a default cache directory for managed PostgreSQL tools."
                    .to_string(),
            ),
        });
    };

    inspect_managed_status_for_root(managed_root).await
}

async fn inspect_managed_status_for_root(
    managed_root: ManagedRoot,
) -> Result<ManagedToolingStatus> {
    let settings = managed_settings(&managed_root.root);
    let version_requirement = settings.version.to_string();
    let installed_versions = installed_versions(&managed_root.root)?;
    let expected_version = resolve_expected_version(&settings).await?;

    let matching = match &expected_version {
        Some(expected) => installed_versions
            .iter()
            .find(|(version, _)| version == expected)
            .cloned(),
        None => installed_versions.first().cloned(),
    };

    let stale_installed_versions = match &expected_version {
        Some(expected) => installed_versions
            .iter()
            .filter(|(version, _)| version != expected)
            .map(|(version, _)| version.to_string())
            .collect(),
        None => installed_versions
            .iter()
            .skip(1)
            .map(|(version, _)| version.to_string())
            .collect(),
    };

    Ok(ManagedToolingStatus {
        root: Some(managed_root.root),
        version_requirement,
        expected_version: expected_version.map(|version| version.to_string()),
        binary_dir: matching.as_ref().map(|(_, path)| path.join("bin")),
        matching_installed_version: matching.as_ref().map(|(version, _)| version.to_string()),
        stale_installed_versions,
        error: None,
    })
}

async fn resolve_expected_version(settings: &Settings) -> Result<Option<Version>> {
    if let Some(version) = settings.version.exact_version() {
        return Ok(Some(version));
    }

    let version = get_version(&settings.releases_url, &settings.version).await?;
    Ok(Some(version))
}

fn installed_versions(root: &Path) -> Result<Vec<(Version, PathBuf)>> {
    if !root.exists() {
        return Ok(vec![]);
    }
    if !root.is_dir() {
        bail!(
            "Managed PostgreSQL root is not a directory: {}",
            root.display()
        );
    }

    let mut versions = Vec::new();
    if let Some(root_version) = parse_version_component(root) {
        versions.push((root_version, root.to_path_buf()));
    }

    for entry in fs::read_dir(root)? {
        let entry = entry?;
        if !entry.file_type()?.is_dir() {
            continue;
        }
        let path = entry.path();
        let Some(version) = parse_version_component(&path) else {
            continue;
        };
        versions.push((version, path));
    }

    versions.sort_by(|(left, _), (right, _)| right.cmp(left));
    versions.dedup_by(|(left_version, left_path), (right_version, right_path)| {
        left_version == right_version && left_path == right_path
    });
    Ok(versions)
}

fn parse_version_component(path: &Path) -> Option<Version> {
    let component = path.file_name()?.to_string_lossy();
    Version::parse(&component).ok()
}

fn inspect_host_status() -> HostToolingStatus {
    let configured_dir = env::var_os("DB_PG_BIN_DIR").map(PathBuf::from);
    let pg_dump = inspect_binary(configured_dir.as_deref(), "pg_dump");
    let pg_restore = inspect_binary(configured_dir.as_deref(), "pg_restore");
    let valid = configured_dir.is_some()
        && pg_dump.present
        && pg_dump.executable
        && pg_restore.present
        && pg_restore.executable;
    let error = configured_dir.as_ref().and_then(|dir| {
        if valid {
            None
        } else {
            Some(format!(
                "DB_PG_BIN_DIR={} must contain executable {} and {} binaries.",
                dir.display(),
                binary_name("pg_dump"),
                binary_name("pg_restore")
            ))
        }
    });

    HostToolingStatus {
        configured_dir,
        valid,
        pg_dump,
        pg_restore,
        error,
    }
}

fn inspect_binary(configured_dir: Option<&Path>, base_name: &str) -> ToolBinaryStatus {
    let path = configured_dir.map(|dir| dir.join(binary_name(base_name)));
    let present = path.as_ref().is_some_and(|path| path.is_file());
    let executable = path.as_ref().is_some_and(|path| is_executable(path));

    ToolBinaryStatus {
        path,
        present,
        executable,
    }
}

fn validate_explicit_host(host: &HostToolingStatus) -> Result<()> {
    if host.configured_dir.is_some() && !host.valid {
        let message = host
            .error
            .clone()
            .unwrap_or_else(|| "DB_PG_BIN_DIR is invalid.".to_string());
        bail!("{message}");
    }
    Ok(())
}

fn build_tooling_status(host: HostToolingStatus, managed: ManagedToolingStatus) -> ToolingStatus {
    let active_backend = if host.valid {
        "host".to_string()
    } else if managed.error.is_none() && managed.root.is_some() {
        "managed".to_string()
    } else {
        "none".to_string()
    };

    let would_download = if active_backend == "managed" {
        match &managed.expected_version {
            Some(expected) => {
                managed.matching_installed_version.as_deref() != Some(expected.as_str())
            }
            None => managed.matching_installed_version.is_none(),
        }
    } else {
        false
    };

    ToolingStatus {
        active_backend,
        host,
        managed,
        would_download,
    }
}

fn maybe_announce_managed_download(managed: &ManagedToolingStatus) {
    if managed.error.is_some() || managed.matching_installed_version.is_some() {
        return;
    }

    let root = managed
        .root
        .as_ref()
        .map(|path| path.display().to_string())
        .unwrap_or_else(|| "<unresolved>".to_string());
    let target = managed
        .expected_version
        .clone()
        .unwrap_or_else(|| managed.version_requirement.clone());
    eprintln!("Managed PostgreSQL tools not installed under {root}; provisioning {target}.");
}

async fn provision_managed_root(install_root: &Path) -> Result<PathBuf> {
    let settings = managed_settings(install_root);
    let mut postgres = PostgreSQL::new(settings);
    postgres.setup().await?;
    Ok(postgres.settings().binary_dir())
}

fn binary_name(base_name: &str) -> String {
    #[cfg(windows)]
    {
        format!("{base_name}.exe")
    }

    #[cfg(not(windows))]
    {
        base_name.to_string()
    }
}

fn is_executable(path: &Path) -> bool {
    let Ok(metadata) = fs::metadata(path) else {
        return false;
    };
    if !metadata.is_file() {
        return false;
    }

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        metadata.permissions().mode() & 0o111 != 0
    }

    #[cfg(not(unix))]
    {
        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn default_root_appends_dotagents_namespace() {
        let root = default_managed_root(PathBuf::from("/tmp/cache"));
        assert_eq!(
            root,
            PathBuf::from("/tmp/cache/dotagents/skills/postgres/postgresql")
        );
    }

    #[test]
    fn unix_cache_base_prefers_xdg_cache_home() {
        let old_home = env::var_os("HOME");
        let old_xdg = env::var_os("XDG_CACHE_HOME");
        unsafe {
            env::set_var("HOME", "/tmp/home");
            env::set_var("XDG_CACHE_HOME", "/tmp/xdg-cache");
        }

        let resolved = default_cache_base_dir();

        match old_home {
            Some(value) => unsafe { env::set_var("HOME", value) },
            None => unsafe { env::remove_var("HOME") },
        }
        match old_xdg {
            Some(value) => unsafe { env::set_var("XDG_CACHE_HOME", value) },
            None => unsafe { env::remove_var("XDG_CACHE_HOME") },
        }

        #[cfg(unix)]
        assert_eq!(resolved, Some(PathBuf::from("/tmp/xdg-cache")));
        #[cfg(not(unix))]
        let _ = resolved;
    }

    #[test]
    fn unix_cache_base_falls_back_to_home_dot_cache() {
        let old_home = env::var_os("HOME");
        let old_xdg = env::var_os("XDG_CACHE_HOME");
        unsafe {
            env::set_var("HOME", "/tmp/home");
            env::remove_var("XDG_CACHE_HOME");
        }

        let resolved = default_cache_base_dir();

        match old_home {
            Some(value) => unsafe { env::set_var("HOME", value) },
            None => unsafe { env::remove_var("HOME") },
        }
        match old_xdg {
            Some(value) => unsafe { env::set_var("XDG_CACHE_HOME", value) },
            None => unsafe { env::remove_var("XDG_CACHE_HOME") },
        }

        #[cfg(unix)]
        assert_eq!(resolved, Some(PathBuf::from("/tmp/home/.cache")));
        #[cfg(not(unix))]
        let _ = resolved;
    }

    #[test]
    fn host_override_wins_over_managed_backend() {
        let host = HostToolingStatus {
            configured_dir: Some(PathBuf::from("/tmp/pg-bin")),
            valid: true,
            pg_dump: ToolBinaryStatus {
                path: Some(PathBuf::from("/tmp/pg-bin/pg_dump")),
                present: true,
                executable: true,
            },
            pg_restore: ToolBinaryStatus {
                path: Some(PathBuf::from("/tmp/pg-bin/pg_restore")),
                present: true,
                executable: true,
            },
            error: None,
        };
        let managed = ManagedToolingStatus {
            root: Some(PathBuf::from("/tmp/cache")),
            version_requirement: "*".to_string(),
            expected_version: Some("18.0.0".to_string()),
            binary_dir: None,
            matching_installed_version: None,
            stale_installed_versions: vec![],
            error: None,
        };

        let status = build_tooling_status(host, managed);
        assert_eq!(status.active_backend, "host");
        assert!(!status.would_download);
    }

    #[test]
    fn invalid_explicit_host_path_errors() {
        let dir = tempdir().unwrap();
        let host = HostToolingStatus {
            configured_dir: Some(dir.path().to_path_buf()),
            valid: false,
            pg_dump: inspect_binary(Some(dir.path()), "pg_dump"),
            pg_restore: inspect_binary(Some(dir.path()), "pg_restore"),
            error: Some("bad host dir".to_string()),
        };

        let error = validate_explicit_host(&host).unwrap_err();
        assert!(error.to_string().contains("bad host dir"));
    }

    #[test]
    fn installed_versions_detects_exact_root_and_children() {
        let root = tempdir().unwrap();
        let exact_root = root.path().join("18.1.0");
        fs::create_dir_all(exact_root.join("bin")).unwrap();
        fs::create_dir_all(root.path().join("17.6.0")).unwrap();
        fs::create_dir_all(root.path().join("note-a-version")).unwrap();

        let versions = installed_versions(root.path()).unwrap();
        assert_eq!(versions[0].0.to_string(), "18.1.0");

        let exact_versions = installed_versions(&exact_root).unwrap();
        assert_eq!(exact_versions[0].0.to_string(), "18.1.0");
        assert_eq!(exact_versions[0].1, exact_root);
    }

    #[test]
    fn managed_backend_marks_missing_expected_version_as_download() {
        let host = HostToolingStatus {
            configured_dir: None,
            valid: false,
            pg_dump: ToolBinaryStatus {
                path: None,
                present: false,
                executable: false,
            },
            pg_restore: ToolBinaryStatus {
                path: None,
                present: false,
                executable: false,
            },
            error: None,
        };
        let managed = ManagedToolingStatus {
            root: Some(PathBuf::from("/tmp/cache")),
            version_requirement: "*".to_string(),
            expected_version: Some("18.2.0".to_string()),
            binary_dir: Some(PathBuf::from("/tmp/cache/17.6.0/bin")),
            matching_installed_version: Some("17.6.0".to_string()),
            stale_installed_versions: vec!["17.6.0".to_string()],
            error: None,
        };

        let status = build_tooling_status(host, managed);
        assert_eq!(status.active_backend, "managed");
        assert!(status.would_download);
    }
}
