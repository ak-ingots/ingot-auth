The mail of the methods goes by the mailer of
[ingot-mail](https://pypi.org/project/ingot-mail/), a new dependency:
`AuthProject` is its `MailProject`, `AuthSettingsUnit`, `AuthLoggingUnit`
and `AuthConfigs` extend those of the mail, so the project declares its
mailer in the slot `mailer` of its `mail` unit, `MemoryMailer` or
`AiosmtplibMailer` of ingot-mail, and the mail goes from `MAIL_FROM`. The
hooks `_build_code_mail()` and `_build_denial_mail()` of
`AuthEmailCodeMethod` return a `Mail` of ingot-mail.
