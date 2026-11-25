A signed-in user changes its password, the old one given:
`Password.ChangePassword` of `ingot_auth.api.methods.password.v1`, `POST
/v1/methods/password:change`, `AuthGrpcPasswordBinding` and
`AuthStarlettePasswordEndpoint`, `CAN_CHANGE` of `auth.methods.password`
granted by `auth.grp_signed_in`. A wrong old password is refused by
`PASSWORD_REFUSED`, `PERMISSION_DENIED`; the new one is checked by
`policies_change` and written on the condition that the hash read is still
there; the other sessions are closed, the change and the closes recorded.
Its event, `AuthPasswordChanged` of the slot `ev_changed`, mails every email
of the profile by default, `_build_changed_mail()` building the mail. The
storages give the identities of a profile, `identities.get_of()`, and
replace a secret on a condition, `secrets.replace()`, which a backend
implements.
