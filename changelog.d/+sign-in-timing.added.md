The timing of the replies of the sign-in, the strategy in the slot `timing`
of `auth.sign_in`, none by default: `AuthFloorTiming` holds a reply of a
start or an answer, a refusal as a success, to `AUTH_SIGN_IN_MIN_DURATION`
seconds, `0.3` by default, so that its time tells nothing of who signed up;
`AuthNoTiming` holds none, the timing of the auth in memory of the addon.
