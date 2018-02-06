# desec-dns-api-cli

A python script utilysing the deSEC.io DNS api to manipulate DNS resource records from the command line.

* [deSEC.io - official website](https://desec.io)
* [deSEC DNS API Documentation](https://desec.io/docs.html)
* [deSEC stack (Github)](https://github.com/desec-io/desec-stack)

This project consist of two components. The deSEC api class handling all requests to the api and there responses. The second component is the command-line script utilising the api class. 

To format the console output, the cli script uses the [tabulate](https://bitbucket.org/astanin/python-tabulate) library which needs to be installed.

    pip install pyyaml tabulate

On macOS, the default python installation requires to install python modules a the following way. 

    sudo python -m pip install pyyaml tabulate


## Configuration

Before requests to the deSEC API can be made, the authorization token need to be configured. Together with the api url, these settings need to be stored in a config file named *desec-dns-cli.yml*. This file should look like this. (en axample config file is available)

    ---
    api_url: https://desec.io/api/v1/domains/
    api_token: 123api456token789

With this settings in the config file, the script / class can access the api.



## Usage 

The scripts functionality is splitted into commands and subcommands. The command defined as "domain" or "rrset" specify the information to manage. The action specifies a specific operation to be performed. This can be "list", "create", "delete" and "modify". 

Not every action is allowed on every command. Some actions require options others allow optional options to be provided. See the complete list of commands, actions and there options below.

    usage: desec-dns-cli.py [-h] [--debug] Command Action [Options]
     
    A python script utilysing the deSEC DNS api to manipulate DNS resource records
    from the command line.
     
    Command, Action and Options:
      domain list             list domains of the account
          --dname DNAME       show a specific domain instead of all   (optional)
     
       domain create          create new domains in the account
          --dname DNAME       specifies the domain name to be created
     
       domain delete          delete domains from the account
          --dname DNAME       specifies the domain name to be deleted
     
      rrset list              list rrsets for a domain
          --dname DNAME       specify the domain / zone to list the rrsets for
          --type TYPE         filter the rrsets by type (A, MX, TXT, ...)   (optional)
          --subname SUBNAME   filter the rrsets by sub-domain / host-part (www, ...)   (optional)
     
      rrset create            create a new rrsets for a domain
          --dname DNAME       specify the domain / zone to add the rrsets to
          --type TYPE         specify the type of the rrset (A, MX, TXT, ...)
          --ttl TTL           specify the ttl in seconds for the rrset
          --subname SUBNAME   specify the sub-domain / host-part for the rrset
          --records RECORDS   specify the records as comma separated list. Text records
                              must contain quotes which requires to state the argument
                              douple-quoted like this '"Text Record 1","Text Record 2"'
                              while MX records contain a priority and a text component,
                              the priority should be outside the second quotes like
                              this '10 "smtp1.domain.tld",20 "smtp2.domain.tld"'
     
      rrset modify            modify a rrsets from a domain
          --dname DNAME       specify the domain / zone to modify the rrsets
          --type TYPE         specify the type of the rrset (A, MX, TXT, ...)
          --ttl TTL           specify the ttl in seconds for the rrset   (optional)
          --subname SUBNAME   specify the sub-domain / host-part for the rrset
          --records RECORDS   specify the records as comma separated list. Text records
                              must contain quotes which requires to state the argument
                              douple-quoted like this '"Text Record 1","Text Record 2"'
                              while MX records contain a priority and a text component,
                              the priority should be outside the second quotes like
                              this '10 "smtp1.domain.tld",20 "smtp2.domain.tld"'   (optional)
        
      rrset delete                delete a rrsets for a domain
          --dname DNAME       specify the domain / zone to modify the rrsets
          --type TYPE         specify the type of the rrset (A, MX, TXT, ...)
          --subname SUBNAME   specify the sub-domain / host-part for the rrset
     
    Global options:
      -h, --help              show this help message and exit
      --debug                 show debug information (optional)
    
    
