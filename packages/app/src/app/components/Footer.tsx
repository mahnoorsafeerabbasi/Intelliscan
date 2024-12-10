import { FC } from "react";
import { makeStyles } from "tss-react/mui";
import { ReactComponent as BackgroundSvg } from "../../assets/bg.svg";
import { ToggleThemeButton } from "./ToggleThemeButton";

export const Footer: FC = () => {
  const { classes } = useStyles();

  return (
    <div className={classes.footer}>
      <div className={classes.footerContent}>
        <ToggleThemeButton />
      </div>
      <BackgroundSvg />
    </div>
  );
};

export const FOOTER_HEIGHT = 80;

const useStyles = makeStyles()((theme) => ({
  footer: {
    position: "fixed",
    bottom: 0,
    width: "100%",
    left: 0,
    display: "flex",
    flexDirection: "column",
    height: FOOTER_HEIGHT,
    background: theme.palette.background.default,
    zIndex: 10,
    alignItems: "center", // Center align content horizontally
    justifyContent: "center", // Center align content vertically
  },
  footerContent: {
    display: "flex",
    alignItems: "center",
    height: '100%',
  },
}));
