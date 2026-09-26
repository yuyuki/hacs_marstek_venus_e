# Agent guidance

This repository is a Home Assistant custom integration in
`custom_components/hacs_marstek_venus_e`. The protocol reference for new work is
`doc/MarstekDeviceOpenApi 3.1.pdf`.
Check the supported devices and firmware notes in the reference before exposing
a command or sensor.

## Marstek protocol

- Use local UDP JSON requests on the configured port. Keep per-device requests
  serialized: the battery frequently times out under overlapping traffic.
- Preserve bounded timeout retries. The current default is two attempts, each
  with a 30-second timeout. Close each attempt's transport even on timeout,
  cancellation, or a malformed response. Never retry forever.
- Distinguish delivery from success. For writes, require `result.set_result`
  to be `true`; a JSON response alone is insufficient.
- Revision 3.1 writes manual slots using `ES.SetMode` with `manual_cfg`.
  `ES.GetSchedule` and `ES.SetSchedule` are undocumented. Do not depend on them.
- `ES.GetStatus.total_pv_energy` is in units of 0.01 kWh (10 Wh).
  Grid import/export and load totals are in Wh. CT energy fields are 0.1 Wh.
- Avoid changing device schedules during configuration or discovery. Clearing
  schedules is an explicit user action after setup.

## Home Assistant behavior

- Register services in `async_setup`, and keep existing automations without a
  target compatible. When a target is supplied, address only that battery.
- Surface rejected writes and exhausted retries to the caller. Optional
  response services can report a result for each battery.
- Keep entity unique IDs and units stable unless the migration of existing
  recorder statistics is addressed explicitly.
- Keep hardware integration tests separate from local unit tests. Never send
  write commands to a real battery during automated tests.

## Verification

- Run `python -m compileall -q custom_components/hacs_marstek_venus_e`.
- Run `python -m unittest discover -s tests -p 'test_unit_*.py'` for tests
  that do not require Home Assistant or a device.
- Check `git diff --check` before committing. Document any behavior that
  still requires validation on a physical device.
