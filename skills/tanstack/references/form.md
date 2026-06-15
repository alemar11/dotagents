# TanStack Form

Use this reference when a task involves `@tanstack/react-form`, form state, `useForm`, `useAppForm`, `form.Field`, `form.AppField`, form validators, field arrays, linked fields, custom errors, form composition, or migrating from React Hook Form.

Use current official TanStack Form docs for exact APIs. TanStack Form favors type safety, composition, and fine-grained subscriptions over direct equivalents to shorter form-library APIs.

## What to Optimize For

- Complete typed `defaultValues` and field paths.
- Controlled headless fields using `field.state.value`, `field.handleChange`, and `field.handleBlur`.
- Validation timing that matches product behavior instead of blindly copying another library's mode.
- Fine-grained reactivity through `form.Subscribe` or `useStore(form.store, selector)`.
- Reusable app-specific form components through `createFormHook` or existing local wrappers.

## React Hook Form Migration Rules

- Do not translate `register` directly. Replace it with TanStack fields or app-bound field components.
- Replace `Controller` patterns with `form.Field`, `form.AppField`, or local wrapper components that bind value, blur, and change handlers.
- Provide complete `defaultValues`; avoid rendering inputs with undefined values while async data is loading.
- Use `mode="array"` on the array field when migrating `useFieldArray`; use array helpers such as `pushValue`, `insertValue`, `replaceValue`, `removeValue`, `swapValues`, and `moveValue`.
- TanStack Form `isDirty` is persistent. Use `isDefaultValue` when you need RHF-style "current value differs from default" behavior.
- For reset controls, prevent native HTML reset behavior or use `type="button"` before calling `form.reset()`.
- Map `mode` and `reValidateMode` behavior to current TanStack validation logic such as `revalidateLogic(...)`, `onDynamic`, and `onDynamicAsync` when the installed version supports them.

## Workflow

1. Inspect current form behavior.
   Capture default values, validation timing, arrays, reset behavior, submit behavior, server errors, and subscriptions before changing code.
2. Choose the form construction pattern.
   Use plain `useForm` for small forms; prefer app-level `createFormHook` or existing wrappers for repeated production forms.
3. Model field state explicitly.
   Wire value, blur, change, touched/error display, disabled state, and submit buttons through TanStack field or subscription APIs.
4. Map validation deliberately.
   Use field/form validators, Standard Schema validators, async validators with debouncing, linked field validation, and form-level `{ fields: ... }` errors where appropriate.
5. Preserve user-facing behavior with tests.
   Test defaults, typing, blur, submit, async validation, arrays, resets, linked fields, custom errors, and submit button state.

## Review Checklist

- Are all fields represented in typed `defaultValues`?
- Do inputs call `field.handleBlur` where blur validation or touched state matters?
- Are async validators debounced with `asyncDebounceMs` or per-validator debounce settings?
- Are errors read from `field.state.meta.errors`, `field.state.meta.errorMap`, or form `errorMap` intentionally?
- Is `disableErrorFlat` used when source-specific error rendering matters?
- Do subscriptions use selectors instead of reading whole form state?
- Are array item keys and array helper calls stable enough for add/remove/reorder flows?

## Avoid

- Keeping RHF concepts like `register`, `watch`, `setError`, or `clearErrors` as hidden compatibility layers unless the app already owns an adapter.
- Showing errors before the product expects them, especially before touch/blur or submit.
- Returning `null` or `false` for valid validators when the current docs expect `undefined`.
- Subscribing a whole component to all form state when only one value or flag is needed.
- Assuming schema validation returns transformed values on submit; parse explicitly when transformed output is needed.

## Verification

Check current TanStack Form docs for Quick Start, Basic Concepts, Validation, Dynamic Validation, Async Initial Values, Arrays, Linked Fields, Reactivity, Listeners, Custom Errors, Submission Handling, Form Composition, Debugging, and framework-specific SSR or TanStack Start guidance.
