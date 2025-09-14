import { env } from './env';

// Dynamically load Clerk script and expose token fetcher
let clerkLoaded: Promise<void> | null = null;

export async function loadClerk() {
  if (typeof window === 'undefined') return;
  if (clerkLoaded) return clerkLoaded;
  clerkLoaded = new Promise((resolve) => {
    const script = document.createElement('script');
    script.setAttribute('async', '');
    script.setAttribute('crossorigin', 'anonymous');
    script.setAttribute('data-clerk-publishable-key', env.clerkPk);
    script.src = `${env.clerkFrontendApi}/npm/@clerk/clerk-js@latest/dist/clerk.browser.js`;
    script.addEventListener('load', async () => {
      // @ts-ignore
      await window.Clerk.load();
      resolve();
    });
    document.head.appendChild(script);
  });
  return clerkLoaded;
}

export async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;
  await loadClerk();
  // @ts-ignore
  const s = window.Clerk?.session;
  if (!s) return null;
  try {
    // @ts-ignore
    const token = await s.getToken({ template: 'default' });
    return token as string;
  } catch {
    return null;
  }
}