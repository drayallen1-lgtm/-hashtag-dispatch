# Setup Checklist — Steps Only You Can Do

Everything else in this project (the logic, the code, the pipeline) is
already built and running. These are the only remaining steps, and they
require your identity, payment method, or signature — I'm not able to do
them on your behalf. Each takes a few minutes.

---

### 1. Create a Twilio account (for phone + text)
- Go to twilio.com, sign up, add a payment method
- Buy one phone number (~$1/month + usage — this becomes the pilot
  business's dispatch number)
- Copy your **Account SID**, **Auth Token**, and the **phone number**
- Send me those three values (or set them as environment variables) and
  I'll wire up `integrations/twilio_client.py` — no other code changes
  needed

### 2. Pick a voice AI platform (for answering calls)
Any of these work with what's already built. Comparison:

| Platform | Notes |
|---|---|
| **Retell AI** | Strong for natural-sounding conversation, good docs |
| **Vapi** | Very developer-friendly, flexible |
| **Bland AI** | Simple pricing, fast to set up |

- Sign up, connect it to your Twilio number
- Copy the API key
- I'll write the call script / system prompt once you've picked one and
  configure `integrations/voice_agent.py` to match

### 3. Line up your first pilot business
- 1 plumbing or HVAC business in Southeast Kansas willing to let you run
  their dispatch for free/cheap during the pilot
- I can draft the outreach message for you whenever you're ready

### 4. (Optional, later) CRM integration
- Only needed once a pilot business already uses ServiceTitan, Jobber, or
  Housecall Pro and wants it connected instead of replaced
- Skip this for the pilot — not needed to launch

---

## What happens after each step
Once you hand me the Twilio credentials, I'll connect the real SMS sending
immediately. Once you pick a voice platform, I'll write the full call
script and wire up the webhook. At that point the system is live and
taking real calls — with zero ongoing manual work beyond the escalation
texts you'll occasionally get.
