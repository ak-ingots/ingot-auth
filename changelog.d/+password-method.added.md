The method of a nickname and a password, `AuthPasswordMethod` in
`ingot_auth.contrib.methods.password`: the nickname and the password
normalized, the password kept as its hash by scrypt of the standard
library and verified on a sign-in, an unknown nickname against a dummy
hash; any nickname and password are taken so far. A method knows its
name, `get_name()`.
