const { render, screen } = require('@testing-library/react');
const HelloWorld = require('./HelloWorld');

test('renders HelloWorld component', () => {
	render(<HelloWorld />);
	const linkElement = screen.getByText(/hello world/i);
	expect(linkElement).toBeInTheDocument();
});