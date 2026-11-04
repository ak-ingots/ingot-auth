The method of a nickname and a password, `AuthNicknameMethod` in
`ingot_auth.methods.nickname`, a method of the core an application binds
as a slot of its methods: the nickname and the password
normalized, the password kept as its hash by scrypt of the standard
library and verified on a sign-in, an unknown nickname against a dummy
hash. Its presets check the nickname and the password of a sign-up, the
context of the password giving its nickname too, `AuthHasNickname`, for a
policy of both. A method knows its name, `get_name()`.
