The method of an email and a code sent to it, of two steps,
`BaseAuthEmailCodeMethod` in `ingot_auth.methods.email_code`: the start
sends a code of random digits by `_send_code()`, the hook an application
implements, and the answer repeats it; the attempt keeps a digest of the
code, not the code. The email is normalized, and checked on a sign-up by
its group of the policies `policies_sign_up_email`. A sign-in sends the
code only to an email bound to a profile, asking for it all the same
otherwise.
