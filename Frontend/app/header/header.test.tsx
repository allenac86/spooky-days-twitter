import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { Header } from './header';

describe('Header component', () => {
  test('renders links for spooky_days_gpt and spooky-days-twitter', () => {
    render(<Header />);

    // Check for the Twitter link
    const twitterLink = screen.getByRole('link', { name: /twitter/i });

    expect(twitterLink).toBeInTheDocument();
    expect(twitterLink).toHaveAttribute('href', 'https://x.com/spooky_days_gpt');

    // Check for the GitHub link
    const githubLink = screen.getByRole('link', { name: /github/i });

    expect(githubLink).toBeInTheDocument();
    expect(githubLink).toHaveAttribute(
      'href',
      'https://www.github.com/allenac86/spooky-days-twitter'
    );

    // Check that SVG icons are present in the links
    expect(twitterLink.querySelector('svg')).toBeInTheDocument();
    expect(githubLink.querySelector('svg')).toBeInTheDocument();
  });
});
