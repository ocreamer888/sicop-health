# so @src/components/Dashboard/FinancialSummaryCard.tsx keeps …

Source: `../../../.cursor/projects/Users-macm1air-Documents-Code-wealth-site/agent-transcripts/0dcb442a-fbfb-4d55-9bb8-c66f011b0d27.jsonl`

---

**User**

<user_query>
so @src/components/Dashboard/FinancialSummaryCard.tsx keeps showing AVAX stats. I want to replace AVAX with USDT balance
</user_query>

---

**Assistant**

I'll help you replace the AVAX stats with USDT balance in the FinancialSummaryCard component. Let me first read the skill file as required, then examine the component.

The user wants to replace AVAX stats with USDT balance in the FinancialSummaryCard component. Let me first read the skill file as required, then look at the component to understand what needs to be changed.

---

**Assistant**

Now let me check how the balance hook works and if there's already a USDT balance hook available.

Now I understand the component. It currently shows AVAX balance using `useWdkBalance` hook. The user wants to replace AVAX with USDT balance. 

Let me check what `useWdkBalance` returns and if there's a way to get USDT balance. I should look at the hook and understand how balances are fetched in this project.

---

**Assistant**

Let me check the token balances hook which likely handles USDT.

I see there's a `useTokenBalances.ts` hook. Let me check that to see if it handles USDT balance fetching.

---

**Assistant**

Let me check the tokens configuration to understand how USDT is set up.

Now I see the token balances hook. Let me also check the tokens config to see how USDT is configured.

---

**Assistant**

Let me find the correct tokens config file.

Hmm, this file seems to have the same content as useWdkBalance.ts - that seems like a mistake. Let me look for the actual tokens config file.

---

**Assistant**

Let me read it again - maybe there's an issue with the file read.

---

**Assistant**

Now I have all the information needed. I'll update the FinancialSummaryCard to use USDT instead of AVAX by replacing the `useWdkBalance` hook with `useTokenBalances`.

Now I have all the information I need. I need to update the `FinancialSummaryCard.tsx` to:
1. Replace the `useWdkBalance` hook (which returns AVAX) with `useTokenBalances` hook to get USDT balance
2. Update the display to show USDT instead of the native currency (AVAX)

Let me make the changes:

---

**Assistant**

Now I need to update the symbol from the dynamic network symbol to "USDT" throughout the component.

---

**Assistant**

Now I need to update the "Available" and "In Escrow" rows to show USDT instead of the symbol variable.

---

**Assistant**

Let me verify the changes look correct.

Now let me verify the changes look correct by reading the updated file.

---

**Assistant**

Let me check for any linter errors.

The changes look good. Let me check for any TypeScript/linter errors.

---

**Assistant**

Done! I've updated the `FinancialSummaryCard` component to display USDT balance instead of AVAX. Here's what changed:

**Changes made to `src/components/Dashboard/FinancialSummaryCard.tsx`:**

1. **Replaced the balance hook**: Changed from `useWdkBalance` (which returns native AVAX balance) to `useTokenBalances` (which fetches ERC20 token balances)

2. **Updated balance extraction**: Now finds the USDT token from the token balances array:
   ```typescript
   const usdtBalance = tokenBalances.find(t => t.config.symbol === "USDT");
   const formattedBalance = usdtBalance?.formattedBalance || "0";
   ```

3. **Updated all symbol displays**: Changed from the dynamic `symbol` variable to static "USDT" labels throughout the component (Total Balance, Available, and In Escrow sections)

The card will now display your USDT token balance instead of AVAX. The balance auto-refreshes every 15 seconds via the `useTokenBalances` hook.

The changes are complete and there are no linter errors. Let me summarize what I changed:

1. Replaced `useWdkBalance` import with `useTokenBalances`
2. Changed from using `formattedBalance` and `symbol` from `useWdkBalance` to finding the USDT token from `tokenBalances` array
3. Updated all symbol displays from the dynamic `symbol` variable to the static "USDT" string

The component now displays USDT balance instead of AVAX balance.

---
