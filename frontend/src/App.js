import React from "react";
import {
  Container,
  Typography,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from "@mui/material";
import PDFUpload from "./components/PDFUpload";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container>
        <Typography variant="h3" component="h1" align="center" sx={{ my: 4 }}>
          PDF Summarizer
        </Typography>
        <PDFUpload />
      </Container>
    </ThemeProvider>
  );
}

export default App;
