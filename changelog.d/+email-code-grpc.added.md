The method of an email and a code over gRPC: the service `EmailCode` of
`ingot_auth.methods.email_code.v1`, `StartSignUp` and `StartSignIn`, in
`AuthGrpcEmailCodeBinding`, and the answers of the flows, whatever the
method, `SignUp.AnswerSignUp` and `SignIn.AnswerSignIn`, in
`AuthGrpcFlowsBinding`, the attempt and the code. The results of the flows
tell what a step asks for, `challenge`, a `Challenge` of
`ingot_auth.methods.v1` by the kind of its answer, `code` of its `length`.
An attempt gone, expired or over is `NOT_FOUND`, the reason
`ATTEMPT_NOT_FOUND`. The servicers of the flows, open to anyone, run
for the anonymous caller of the project whatever a call bears.
