import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Grid, Typography, Paper } from "@material-ui/core";

/**
 * Displays the about page in our app
 *
 * @author [Lukas Rutkauskas] (https://github.com/LukasRutkauskas)
 */

export default function About() {
  const classes = useStyles();
  return (
    <div align="center">
      <Paper className={classes.page}>
        {/*The Grid container was used to display every paragraph in a new line */}
        <Grid container direction="column">
          <Grid item>
            <Typography variant="h5" align="left">
              Unsere App
            </Typography>
          </Grid>
          <Grid item>
            <Typography
              variant="body1"
              align="left"
              className={classes.paragraph}
            >
              Dies ist die App für unseren Empfehlungsalgorithmus im Rahmen des
              Big Data Projekts. Die App wurde mithilfe von React sowie Material
              UI erstellt. Sie ist durch eine Flask API mit der Datenbank
              verbunden, und greift mithilfe von dieser auf alle Daten zu.
            </Typography>
          </Grid>
          <Grid item className={classes.heading}>
            <Typography
              variant="h6"
              align="left"
              style={{ fontWeight: "normal" }}
            >
              Autoren
            </Typography>
          </Grid>
          <Grid item className={classes.paragraph}>
            <Typography variant="body1" align="left">
              Jonas Wagenknecht
            </Typography>
          </Grid>
          <Grid item>
            <Typography variant="body1" align="left">
              jw126@hdm-stuttgart.de
            </Typography>
          </Grid>
          <Grid item className={classes.paragraph}>
            <Typography variant="body1" align="left">
              Helena Nebel
            </Typography>
          </Grid>
          <Grid item>
            <Typography variant="body1" align="left">
              hn010@hdm-stuttgart.de
            </Typography>
          </Grid>
          <Grid item className={classes.paragraph}>
            <Typography variant="body1" align="left">
              Larisa Ciupe
            </Typography>
          </Grid>
          <Grid item>
            <Typography variant="body1" align="left">
              lc030@hdm-stuttgart.de
            </Typography>
          </Grid>
          <Grid item className={classes.paragraph}>
            <Typography variant="body1" align="left">
              Lukas Rutkauskas
            </Typography>
          </Grid>
          <Grid item>
            <Typography variant="body1" align="left">
              lr057@hdm-stuttgart.de
            </Typography>
          </Grid>
          <Grid item className={classes.paragraph}>
            <Typography variant="body1" align="left">
              Ardian Fejzullahu
            </Typography>
          </Grid>
          <Grid item>
            <Typography variant="body1" align="left">
              af085@hdm-stuttgart.de
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </div>
  );
}

const useStyles = makeStyles((theme) => ({
  page: {
    width: "51em",
    height: "60em",
    paddingTop: "2em",
    paddingBottom: "1em",
    paddingLeft: "10em",
    paddingRight: "10em",
  },
  paragraph: {
    marginTop: "1em",
  },
  heading: {
    marginTop: "2em",
  },
}));
