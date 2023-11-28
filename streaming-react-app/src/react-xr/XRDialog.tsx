import {
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import XRConfig, {XRConfigProps} from './XRConfig';
import {useState} from 'react';
import './XRDialog.css';

export default function XRDialog(props: XRConfigProps) {
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  return (
    <>
      <Button variant="contained" onClick={() => setIsDialogOpen(true)}>
        Enter AR Experience
      </Button>
      <Dialog onClose={() => setIsDialogOpen(false)} open={isDialogOpen}>
        <DialogTitle sx={{m: 0, p: 2}} className="xr-dialog-text-center">
          FAIR Seamless Streaming Demo
        </DialogTitle>
        <IconButton
          aria-label="close"
          onClick={() => setIsDialogOpen(false)}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}>
          <CloseIcon />
        </IconButton>
        <DialogContent
          dividers
          className="xr-dialog-container xr-dialog-text-center">
          <Typography gutterBottom>
            Welcome to the Seamless team streaming demo experience! In this demo
            you will experience AI powered text and audio translation in real
            time.
          </Typography>
          <XRConfig {...props} />
        </DialogContent>
      </Dialog>
    </>
  );
}
