You need to generate a key to sign your transactions.

Use `sawtooth keygen <file_name>` command.
Copy the priv key to new property in odoo.conf like

`sawtooth_key = $HOME/.sawtooth/keys/<file_name>.priv`