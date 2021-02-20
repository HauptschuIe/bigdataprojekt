import React from 'react';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';

const useStyles = makeStyles((theme) =>
  createStyles({
    formControl: {
      margin: theme.spacing(1),
      minWidth: 120,
    },
    selectEmpty: {
      marginTop: theme.spacing(2),
    },
  }),
);

export default function SimpleSelect(props) {
    const classes = useStyles();
    
    const [age, setAge] = React.useState('');

    const handleChange = (event) => {
      setAge(event.target.value);
    };
   return (
    <div>
      <FormControl className={classes.formControl}>
        <InputLabel id="demo-simple-select-label">Search by</InputLabel>
        <Select
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          value={age}
          onChange={handleChange}
        >
          <MenuItem value={"all-recipes"}>List</MenuItem>
          <MenuItem value={"recipes-by-name"}>Name</MenuItem>
          <MenuItem value={"see-what-else-the-author-published"}>Author</MenuItem>
          <MenuItem value={"see-what-other-users-rated"}>What others rated</MenuItem>
          <MenuItem value={"similar-recipes-based-on-ingredients"}>Ingredients</MenuItem>
        </Select>
      </FormControl>
      </div>
      );
}