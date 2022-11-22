import React, { Component } from "react";
import { render } from "react-dom";

class App extends Component {
	constructor(props) {
		super(props);
		this.state = {
			data: [],
			loaded: false,
			placeholder: 'Loading',
		};
	}

	componentDidMount() {
		fetch('authors')
			.then((response) => {
				if (response.status > 400) {
					return this.setState(() => {
						return { placeholder: 'Something went wrong!' };
					});
				}
				return response.json();
			})
			.then((data) => {
				this.setState(() => {
					return {
						data: data?.items ?? [],
						loaded: true,
					};
				});
			});
	}

	render() {
		return (
			<ul>
				{this.state.data.map((user) => {
					return (
						<li key={user.id}>
							{user.id} - {user.displayName}
						</li>
					);
				})}
			</ul>
		);
	}
}

export default App;

const container = document.getElementById("app");
render(<App />, container);