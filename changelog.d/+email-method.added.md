The method of an email and a code sent to it, of two steps,
`BaseAuthEmailMethod` in `ingot_auth.contrib.methods.email`: the start
sends a code of random digits by `_send_code()`, the hook an application
implements, and the answer repeats it; the attempt keeps a digest of the
code, not the code. The email is normalized, and checked on a sign-up by
the preset `preset_sign_up_email`. A sign-in sends the code only to an
email bound to a profile, asking for it all the same otherwise. A method
checks a value by its preset with `_check_value()`.
