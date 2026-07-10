# Release Checklist

## v2.14.1.1 Testliste

### No Refresh
- [ ] ADD ACTION does not reload the whole page
- [ ] UPDATE ACTION does not reload the whole page
- [ ] MOVE UP / MOVE DOWN does not reload the whole page
- [ ] DELETE does not reload the whole page

### WAIT
- [ ] Add WAIT with 3 seconds
- [ ] RUN PRESET
- [ ] Status shows WAITING
- [ ] Countdown/remaining time changes
- [ ] Next action starts after 3 seconds
- [ ] Log shows WAIT and WAIT finished
- [ ] STOP during WAIT aborts the preset

### Regression
- [ ] F8 works
- [ ] Banner + Text work
- [ ] Scene Switch works
- [ ] OBS Workflow does not flicker
- [ ] Live Card works
