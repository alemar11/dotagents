# Common API Shaping Patterns

Use this page when the guideline question is less about a single name and more
about a recurring API cleanup move.

For exact official wording and examples, open
[api-design-guidelines.md](../assets/api-design-guidelines.md).

## Replace a raw `Bool` with a named type

Prefer a named enum or options type when a `Bool` hides meaning at the call
site.

Prefer:
- `loadData(from:cachePolicy:)`
- `dismiss(animated:)`
- `FeatureFlags.Options(fallbackValue:cacheDuration:)`

Avoid:
- `loadData(_:, cache: true)`
- `save(_: overwrite: false)` when the meaning of `false` is unclear

Rule of thumb:
- keep a `Bool` only when the label alone makes the meaning obvious
- promote to an enum or options type when the choice has domain meaning or may
  grow later

## Prefer stronger domain types over loose primitives

Use `URL`, small wrapper types, or focused value types when `String`, `Int`, or
`Any` would force the call site to carry too much ambiguity.

Prefer:
- `loadData(fromFileURL:)` over `data(_ path: String)`
- `Feature("new_checkout")` over a bare string key everywhere
- `PhoneNumberInput` over passing separate raw strings around

Ask:
- does the primitive force the reader to guess the semantic role?
- would a tiny wrapper make the API safer and easier to document?

## Name protocols for identity or capability

Prefer nouns for identity-style protocols and `able`, `ible`, or `ing`
capability names when the protocol describes what a type can do.

Prefer:
- `Collection`
- `FeatureFlagProviding`
- `DataLoading`

Avoid:
- `LoaderProtocol`
- `FeatureFlagProtocol`

## Use options bags for secondary knobs

Introduce an `Options` type when several secondary parameters travel together
or defaulting them individually would make the primary call harder to read.

Prefer:
- `FeatureFlags(provider:options:)`
- `Renderer.Options(scale:backgroundColor:)`

Avoid:
- long public initializers where every secondary toggle is a separate
  parameter unless those values are central to the call

Rule of thumb:
- use direct parameters for 1-2 central values
- use an options bag when the configuration is supportive rather than central

## Choose between property, method, initializer, and factory by meaning

Use the API form that matches the semantics:

- property or nonmutating method for values or queries
- mutating method for in-place change
- initializer for creating a value directly
- factory method when the returned thing has a role best explained by a verb
  like `make`

Quick checks:
- If it reads like a value, make it a property or noun-like method.
- If it changes state, make it a verb.
- If it returns a modified copy, pair it with a mutating form when helpful.
- If an initializer label starts carrying too much narrative, consider whether
  a factory method is clearer.

## Prefer clear edit operations over overloaded formatter families

For text-entry APIs, model the editing action directly when that makes the call
site easier to understand.

Prefer:
- `editedInput(for:replacingCharactersIn:with:)`
- `formattedText(from:)`
- `sanitizedDigits(from:)`

Avoid:
- several overloaded `format(_:)` methods whose roles blur together

## Common review moves

When reviewing an awkward API, check these first:

- replace ambiguous `Bool` parameters with domain names
- replace weakly typed `String` or `Any` inputs with stronger roles
- rename protocols away from `*Protocol`
- split semantic overloads into clearer names
- collapse same-behavior method families into one API with defaults
- add or tighten a mutating/nonmutating pair when the operation naturally has
  both forms

## Fast Path

- Use [naming-and-signatures.md](naming-and-signatures.md) for label, default,
  and overload guidance.
- Use [review-checklist.md](review-checklist.md) when auditing an existing API
  surface end to end.
