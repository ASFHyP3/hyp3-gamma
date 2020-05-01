## Description of the merge request


<!--
Please describe the merge request here. Indicate *why* you chose the solution you did and any 
alternatives you considered
-->

<!--
If applicable, indicate any upstream packages/projects this is relevant too, and the associated issues
or merge requests
-->

### Developer checklist

- [ ] Assigned a reviewer
  <!-- NOTE: Merge requests should only be opened for merges to protected branches (required) and any 
   changes which you'd like reviewed. Do not open a merge request to update a feature or personal
   branch -- simply merge with `git`.
   -->
- [ ] Indicated the level of changes to this package by affixing one of these labels:
  * ~"major" -- Major changes to the API that may break current workflows
  * ~"minor" -- Minor changes to the API that do not break current workflows 
  * ~"patch" -- Patches and bugfixes for the current version that do not break current workflows
  * ~"bumpless" -- Changes to documentation, CI/CD pipelines, etc. that don't affect the software's version 
  
  See: [Hyp3 Development Guidelines](https://wiki.asf.alaska.edu/x/WwBOB) for a detailed discussion of these levels

- [ ] (If applicable) Updated the dependencies and indicated any downstream changes that are required 

- [ ] Updated the CHANGELOG
- [ ] Added/updated documentation for these changes
- [ ] Added/updated tests for these changes

### Reviewer checklist

- [ ] Is the CI/CD pipeline passing?
- [ ] Have all dependencies been updated and required changes merged downstream?
- [ ] Is the level of changes labeled appropriately?
- [ ] Are all the changes described appropriately in the changelog?
- [ ] Has the documentation been adequately updated?
- [ ] Are the test adequate?