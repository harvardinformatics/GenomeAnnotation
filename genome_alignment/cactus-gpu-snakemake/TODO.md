# TODO

1. ~~Implement jobs by rounds instead of strict post-order traversal of intput tree~~ Completed 4.25.2022
2. ~~Add resource options to config~~ Completed 8.4.2022
3. ~~halAppend steps~~ Completed 7.7.2022
4. ~~Test various issues (e.g. the --restart flag, --configFile)~~ Completed 8.4.2022
5. ~~Add a rule to copy the final HAL file before appending the other HALs to it so it that step doesn't have to be re-done if the later steps need to be re-run~~ Completed 8.4.2022
6. ~~Add a rule to convert the final HAL to MAF~~ Defunct 8.24.2022, this will be done with Comparative Augustus
7. ~~Add a non-gpu option for the mask and blast rules~~ Completed 8.24.2022
8. ~~Update to cactus 2.2.0~~ Completed 8.24.2022
9. Add in a workflow to add a genome to an alignment (https://github.com/ComparativeGenomicsToolkit/cactus/blob/master/doc/cactus-update-prepare.md)