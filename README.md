<p align="center"><img src="logo.png" align="middle"></img></p>

# What is S&Box Notifier?
S&Box Notifier is a Discord webhook programmed to send an alert when it detects keys available in the 'Developer Preview Torture Service' in order to redeem an access key to the new Facepunch game, S&Box, which is currently in a closed BETA. Good luck to you all!

# How do I use S&Box Notifier?
You can use S&Box Notifier by either joining the <a title="Discord server" href="https://discord.gg/jyy8HMdbEA">Discord server</a>, or you can [host the script yourself](#hosting) and use it in a private server. 

# Hosting
To run your own instance of S&Box Notifier you need to have docker and git installed on your system and follow these steps:

1. Clone the repository.
    ```
    git clone https://github.com/yyewolf/S-Box-Notifier.git
    ```
2. Go into the cloned repository folder and edit the file "docker-compose.yml" and add to the following lines:
    ```
            - WEBHOOK_URL=insert webhook url for the notifications channel
            - WEBSITE_URL=https://asset.party/get/developer/preview
            - WEBHOOK_LOG_URL=insert webhook url for the scans channel
            - POLL_RATE=amount of seconds per scan.(60 recommended)
    ```
3. Compose a docker container with this command while inside the repository folder:
    ```
    docker compose up -d
    ```

The docker container is now running and the webhook should now be updating your server!

# Uninstalling
If you want to uninstall the script do the following:

1. Stop the docker container.
    ```
    docker stop s-box-notifier-app-1
    ```

2. Remove the docker container.
    ```
    docker rm s-box-notifier-app-1
    ```
3. Delete the repository folder.

# Can I contribute to the project?
Feel free to send your proposals and the community will take care of accepting them. Together we can improve the functionality of this tool.

# Discord Server
Join our official Discord server by <a title="Discord server" href="https://discord.gg/jyy8HMdbEA">clicking here</a>
