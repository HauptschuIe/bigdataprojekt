import React, { Component } from "react";
import { withStyles } from "@material-ui/core/styles";
import { Typography, Tabs, Tab, Paper } from "@material-ui/core";
import { Link as RouterLink } from "react-router-dom";

class Header extends Component {
  constructor(props) {
    super(props);

    this.state = {
      tabindex: 0,
    };
  }

  //Changes the tabindex if you select another tab

  handleTabChange = (e, newIndex) => {
    this.setState({
      tabindex: newIndex,
    });
  };

  render() {
    const { classes } = this.props;

    return (
      <div align="center">
        <Paper className={classes.heading}>
          <Typography variant="h4">Chefkoch Empfehlungsalgorithmus</Typography>
        </Paper>
        <Paper className={classes.body}>
          {/* Displays the tabs in the header */}
          <Tabs
            indicatorColor="primary"
            textColor="primary"
            value={this.state.tabindex}
            onChange={this.handleTabChange}
            style={{ marginBottom: "2em" }}
            centered
          >
            <Tab label="Alle Rezepte" component={RouterLink} to={`/`} />
            <Tab
              label="Rezeptsuche"
              component={RouterLink}
              to={`/recipes-by-name`}
            />
            <Tab
              label="Rezepte eines Autors"
              component={RouterLink}
              to={`/recipes-from-an-author`}
            />
            <Tab
              label="Kollaborative Empfehlungen"
              component={RouterLink}
              to={`/recommendations-based-on-user-ratings`}
            />
            <Tab
              label="Content-Empfehlungen"
              component={RouterLink}
              to={`/recommendations-based-on-ingredients`}
            />
            <Tab label="Über uns" component={RouterLink} to={`/about`} />
          </Tabs>
        </Paper>
      </div>
    );
  }
}

//Styling of the components

const styles = (theme) => ({
  heading: {
    color: "#000000",
    padding: "30px",
  },
});

export default withStyles(styles)(Header);
