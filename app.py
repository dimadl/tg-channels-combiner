import json, logging, sys
from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import CreateChannelRequest

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',level=logging.INFO)

with open('config.json') as config_file:
    data = json.load(config_file)
    logging.info('Config file has been initialized.')

app_id = data['app_id']
app_hash = data['app_hash']

def warm_up():
    logging.info('First run')
    with TelegramClient('session2', app_id, app_hash) as client:
        user = client.get_me()
        logging.info('Singed in as {} {}'.format(user.first_name, user.last_name))

def main():
    with TelegramClient('session2', app_id, app_hash) as client:
        chats_combiners = data['new_channels']
        
        for channel in chats_combiners:
            channel_name = channel['channel_name']

            logging.info('Initializing the channel: {}'.format(channel_name))

            try:
                channel_entity = client.get_entity(channel_name)
                logging.info('Channel {} exists'.format(channel_name))
            except ValueError:
                client(CreateChannelRequest(channel_name,"about",megagroup=False))
                channel_entity = client.get_entity(channel_name)
                logging.info('Channel has been created: {}'.format(channel_name))

            channels_to_be_combined = channel['channels_to_be_combined']

            for channel_injected in channels_to_be_combined:

                logging.info('Messages from {} are being forwarded to {}'.format(channel_injected, channel_name))

                @client.on(events.NewMessage(channel_injected))
                async def handler(event):
                    logging.debug('Message from {}: {}'.format(channel_injected, event.message.message))
                    await client.forward_messages(channel_entity,event.message)

        client.run_until_disconnected()

if len(sys.argv) > 1 and sys.argv[1] == "w":
    warm_up()
else:
    main()