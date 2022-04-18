import atoot
import asyncio
import json
import pprint
instance = "mastodon.online"
access_token = "hunter2"

async def parse_notification(notif,stream,c):
    #payload = json.loads(payload.json())
    #print(notif)
    if stream == 1:
        #coming from the live stream
        #print("stream msg")
        #print(notif["payload"])
        notif = json.loads(notif["payload"])
    #Is it a mention?
    pprint.pprint(notif)
    print("***********************************************")
    try:
        if notif["type"] == "mention":
            #private_toot()
            content = notif['status']['content'].split('class="u-url mention">')[1].replace("</p>","")
            print(f"we have been mentioned by user {notif['account']['id']} \nContents of the msg: {content}")
            op_account_id = notif['status']['in_reply_to_account_id']

            #We where mentioned publicly
            if notif['status']["visibility"] == "public":
                #make sure we where mentioned, in a reply 
                if op_account_id:
                    #this is a reply to someone (who is probably being tipped xmr)
                    get_op = await atoot.MastodonAPI.account(c,account=op_account_id)
                    op_username = get_op["username"] 
                    print(f"The OP = {op_username}")
                    await handle_tipxmr(op_username,content)

            #someone sent a direct message
            if notif['status']["visibility"] == "direct":
                print("direct message detected lol")
                #the OP will be ourselves, so get the correct username
                username = notif["status"]["account"]["username"]
                print(f"username = {username}")
                await handle_direct_message(username,content)

        print("***********************************************")
        return
    except:
        pass
    print("***********************************************")

async def handle_tipxmr(username,content):
    global access_token, instance
    async with atoot.client(instance, access_token=access_token) as c:
        msg_content = f"hello world @{username} you have been tipped some Monero"
        await c.create_status(status=msg_content,visibility="direct")

async def handle_direct_message(username,content):
    global access_token, instance
    async with atoot.client(instance, access_token=access_token) as c:
        msg_content = f"hello world @{username} you probably want to create an XMR address"
        await c.create_status(status=msg_content,visibility="direct")

async def mastodon_bot():
    global instance
    global access_token
    async with atoot.client(instance, access_token=access_token) as c:
        #via a cron job (also, maybe we lost connection and have to check all of our notifications etc)
        notifs = await c.get_all(c.get_notifications())
        for x in notifs:
            await parse_notification(x,0,c)
        #or via websocket / live streaming
        async with c.streaming("user") as ws:
            async for msg in ws:
                await parse_notification(msg.json(),1,c)

asyncio.run(mastodon_bot())

'''
async def _account_info(self, account, info="", **kwargs):
        return await self.get(
                '/api/v1/accounts/%s/%s' % (get_id(account), info), **kwargs)
'''

#notification -> mention
#in reply to
#content

#if someone mentions tipxmr - parse the toot - whoever it was in_reply_to gets the money

#crate_status -> in_reply_to_id
