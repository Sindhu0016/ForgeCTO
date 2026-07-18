const rawKey = (import.meta.env.VITE_CLERK_PUBLISHABLE_KEY as string | undefined)?.trim() ?? "";

/** True when a real Clerk publishable key is present (not empty / placeholder). */
export const isClerkConfigured =
  /^pk_(test|live)_/.test(rawKey) && !rawKey.includes("your_key");

export const clerkPublishableKey = isClerkConfigured ? rawKey : "";
