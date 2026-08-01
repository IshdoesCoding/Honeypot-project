Phase 1:

Fixed three bugs in ssh_honeypot.py:

1. HOST_KEY undefined (was the direct cause of your Connection reset by peer) — the code referenced HOST_KEY but only host_key (a filename string) existed. Now loads it properly: HOST_KEY = paramiko.RSAKey.from_private_key_file(host_key).
2. paramiko.Transport() missing the socket arg — needed paramiko.Transport(client), otherwise every connection crashed right after auth.
3. Indentation bug in emulated_shell — the send/reset block ran after every keystroke instead of only after Enter, causing a NameError: response on the first character typed.

I also regenerated server.key/server.key.pub without a passphrase (the old one required one paramiko couldn't supply, per your choice).

Verified with a Python/paramiko test client: login succeeds, whoami returns usr correctly. You can now run python3 ssh_honeypot.py and connect with ssh -p 2223 username@127.0.0.1 (password: password).

One minor pre-existing quirk I didn't touch since it's unrelated to your reported issue: typing exit closes the channel before the "Goodbye!" message is sent, and the server logs a harmless "Socket is closed" error afterward. Let me know if you'd like that cleaned up too.