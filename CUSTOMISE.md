# Make it yours

## 1. Get your own copy
- **Fork** this repo on GitHub, then install the plugin from your fork instead (`your-name/pe-deal-desk`).
- Forks of public repos stay public. **Never commit confidential deal material.** Keep firm templates and deal files on your computer, or in a private repo created with GitHub's **Import repository**.

## 2. Edit a skill
Each skill is a plain-English `skills/<name>/SKILL.md`. Change it in either of these ways:
- **On GitHub:** open the file, click the pencil icon, edit the text, then click **Commit**.
- **With Claude:** open your copy in the Claude Desktop **Code** tab and ask for the change (see the prompts below).

After any change, raise `version` in `.claude-plugin/plugin.json`, then update the plugin in **Customize → Plugins**.

## 3. Add your data (MCPs)
Connect the data providers you already pay for under **Customize → Connectors**: PitchBook, S&P Capital IQ, FactSet and others. Then tell the relevant skill to use them, e.g. in `comps-valuation`: *"If a PitchBook or Capital IQ connector is available, pull peer data from it and cite the source."*

## Prompts to copy
- "Add our IC template (attached) to the ic-memo skill and make it the default structure."
- "Here are our fund criteria. Save them as a reference file in cim-screen and use them in every screen."
- "Add management rollover and a revolver to the LBO model. Test it, then push."
- "The screen missed X on this deal. Update cim-screen so it checks for that."
- "Create a new skill for [task] that works like the others."
- "Add a [sector] section to diligence-plan with the requests we always make."

**Test** each change on a past deal where you already know the answer.
