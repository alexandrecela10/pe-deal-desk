# PE Deal Desk — start here

Six private equity skills for Claude. Install once, then just talk to Claude normally — it picks the right skill on its own. No coding, no GitHub, no terminal.

## Install (2 minutes)

1. Open the **Claude desktop app** (or claude.ai in a browser).
2. Go to **Settings → Capabilities** and make sure **Code execution and file creation** is switched **on**. (The skills need it to run their calculations.)
3. In the sidebar, open **Customize → Plugins**, click **Add**, then **Upload plugin**, and choose the file **`pe-deal-desk.zip`**.
4. Done. You should see **pe-deal-desk** in your plugins list with six skills switched on.

**If you don't see "Upload plugin":** unzip `individual-skills.zip`, then go to **Customize → Skills**, click **+**, choose **Upload a skill**, and upload each of the six small zip files one at a time.

## Use it

Start a new chat (or a Cowork task) and ask in plain English. Attach files when you have them.

| You want to… | Try saying |
|---|---|
| Get a first view on a deal | "Here's the CIM. Screen it — pass or pursue?" |
| Check returns / price | "Quick LBO: £40m EBITDA, 10x entry, 5x leverage, 5-year hold. What can we pay for a 20% IRR?" |
| Value a company | "Here's a comps export. What's the target worth on 42m EBITDA?" |
| Plan diligence | "We're in exclusivity. Build the diligence plan and the information request list." |
| Write the IC paper | "Draft the IC memo using everything we've done on this deal." |
| Review a portfolio company | "Here's this month's pack. Anything red? How's our covenant headroom?" |

Tips:
- Keep one chat (or one Project) per deal, so the memo can reuse the screen, LBO and comps.
- Tell Claude your fund's criteria once (cheque size, sectors, EBITDA range) and ask it to use them.
- You can always say "use the lbo-model skill" if Claude doesn't pick it on its own.

## Confidentiality

CIMs and deal documents are confidential. Only upload them to a Claude account your firm has approved for deal data, and check the NDA first.
