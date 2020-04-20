# Nagios/Icinga2 Plugin: check_borgmatic 
Python3 plugin for borgmatic to check the last successful backup.
```
$ /usr/lib64/nagios/plugins/check_borgmatic/check_borgmatic.py -w 86400 -c 172800
OK - last borgmatic backup: 2020-04-20 01:58:12 (age: 18:13:22.123227) with name www-2020-04-20T01:58:09 | 'lastbackup_s'=65602
```

# Requirements: 
- sudo installed: `apt install sudo` 

# Install
## manually  
- Clone this repo: `git clone https://github.com/chris2k20/check_borgmatic /usr/lib64/nagios/plugins/check_borgmatic`
- configure nagios-user to execute sudo borgmatic as root: `echo "nagios ALL= NOPASSWD:/usr/local/bin/borgmatic --list --successful --last 1 --json" | tee /etc/sudoers.d/nagios_borgmatic`

## ansible
_Not jet, this part will follow.._

# Configure Icinga2 
Here are some examples to integrate this plugin into your Icinga2 environment:

`vim /etc/icinga2/conf.d/commands.conf`
    
    object CheckCommand "check_borgmatic" {
            import "plugin-check-command"
            command = [ PluginDir + "/check_borgmatic/check_borgmatic.py" ]

            arguments = {
                    "-c" = {
                            value = "$borgmatic_critical$"
                            description = "Specifies the ciritcal seconds"
                    }
                    "-w" = {
                            value = "$borgmatic_warning$"
                            description = "Specifies the warning seconds"
                    }
            }
            # Defaults
            vars.borgmatic_warning = 2d
            vars.bogmatic_critical = 5d
    }

`vim /etc/icinga2/conf.d/services.conf` (you have to customize the following)

    apply Service "Linux-Borgmatic" {
        check_command = "check_borgmatic"
        import "ssh-service"
        vars.by_ssh_port = host.vars.ssh_port
        vars.by_ssh_timeout = 60
        check_timeout = 2m
        check_interval = 1h
        retry_interval = 1h
        max_check_attempts = 2
        assign host.vars.borgmatic == true
    }

# Developers 
Please feel free to customize this. Thank you :) 
