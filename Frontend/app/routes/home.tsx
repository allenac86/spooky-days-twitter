import type { Route } from './+types/home';
import { Welcome } from '../welcome/welcome';

export function meta({}: Route.MetaArgs) {
  return [
    { title: 'spooky-days-gpt' },
    { name: 'description', content: 'Welcome to the Spooky Days Gallery!' },
  ];
}

export default function Home() {
  return <Welcome />;
}
