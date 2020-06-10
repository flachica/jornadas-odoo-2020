==========================
Blockchain Proxy
==========================

With this module you will be able to read, write and execute smart contracts in a Hyperledger Sawtooth based Blockchain network

**Table of contents**

.. contents::
   :local:

Installation
============

You can find the python dependencies in manifest file of this module

[+INFO](https://sawtooth.hyperledger.org/docs/core/releases/latest/app_developers_guide/ubuntu.html)

Configuration
=============

You need to generate a key to sign your transactions.

Use `sawtooth keygen <file_name>` command.
Copy the priv key to new property in odoo.conf like

`sawtooth_key = $HOME/.sawtooth/keys/<file_name>.priv`

Usage
=====

To use this module, you need to:

* Enable Debuging Mode
* Up your Sawtooth docker image with <sawthooth_plugins>/docker-compose.yaml file
* Go to Settings -> Blockchain -> Blockchain reader to Read or Write on your network

In <sawtooth_plugins>/processors/families you can find the Generic Family (Smart Contract) as simple example use case

Credits
=======

Authors
~~~~~~~

* Guadaltech Soluciones Tecnológicas <https://www.guadaltech.es/>

Contributors
~~~~~~~~~~~~

* `Guadaltech Soluciones Tecnológicas <https://www.guadaltech.es/>`_:

  * Fernando La Chica <fernando.lachica@guadaltech.es>
  * Ramón Bajona <ramon.bajona@guadaltech.es>