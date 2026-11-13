# Configs

Set as environment variables with the prefix of the project
(`APP_AUTH_LOGGING_LEVEL`), in a `--configs-file` or with `--config`.

| Name | Default | Meaning |
|---|---|---|
| `AUTH_LOGGING_LEVEL` | `INFO` | the level of the logger of the addon, `ingot_auth` |
| `AUTH_ATTEMPT_TTL` | `600` | the seconds an attempt of a sign-up, a sign-in waits for an answer |
| `AUTH_ATTEMPT_MAX_FAILURES` | `5` | the answers refused before an attempt is over |
| `AUTH_SESSION_TTL` | `2592000` | the seconds a session of a fixed lifetime lives from its sign-in, 30 days |
| `AUTH_SESSION_IDLE_TTL` | `3600` | the seconds a session of a sliding lifetime lives idle, an hour |
| `AUTH_SESSION_TOUCH_INTERVAL` | `300` | the seconds between two writes of the time a session of a sliding lifetime is seen at, well below the idle TTL |
| `AUTH_SESSION_CACHE_TTL` | `300` | the seconds a session and its caller stay in the cache |
| `AUTH_SIGN_UP_ENABLED` | `on` | the toggle of the sign-up by every method: off, no one signs up, whatever the toggles of the methods |
| `AUTH_SIGN_IN_MIN_DURATION` | `0.3` | the seconds a step of the sign-in replies no sooner than, with `AuthFloorTiming` |

A method bound brings the toggles of its flows, `AUTH_SIGN_UP_<METHOD>_ENABLED`
and `AUTH_SIGN_IN_<METHOD>_ENABLED`, on by default ({doc}`methods`).
