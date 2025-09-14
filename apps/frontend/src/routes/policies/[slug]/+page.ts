import type { PageLoad } from './$types';
import { env } from '$lib/env';

export const load: PageLoad = async ({ params, fetch }) => {
  const res = await fetch(`${env.backendBase}/cms/${params.slug}`);
  const data = await res.json();
  return { page: data };
};