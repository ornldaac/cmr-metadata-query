# How to contribute

## Testing

All code should be covered with appropriate unit tests. Unit tests should be implemented in a Python file named like the tested file with a "test_" prefix (i.e. `mycode.py` should be tested in `test_mycode.py`). Add new test files to the CI pipeline by editing [.gitlab-ci.yml](.gitlab-ci.yml). Group individual aspects of the tested code into test cases.

Make sure any new code is fully tested. Test coverage is measured by the CI pipeline. Refer to [.gitlab-ci.yml](.gitlab-ci.yml) to see how coverage is measured and analyze coverage locally before committing.

Here are some additional guidlines:

* Don't assume any specific output when testing, but instead perform sanity checks on the returned data.

  *Example:* Don't check if request `a` to a web service with parameters `b` returns output `c`. Instead test if `c` contains reasonable values). This way unit tests won't break if output is updated in the future.
* Make sure tests are deterministic.

  *Example:* Don't validate a random subset of valid inputs to a web service. Such tests are hard to reproduce and they may cause the CI pipeline to report errors when committing unrelated changes in the future.

## Submitting changes

### Git workflow

Create a new issue for any bug reports or feature requests. Create a feature branch to resolve the bug or implement the feature. After successful [testing](#Testing), merge the feature request back into the main branch using a [merge request](#Merge-Requests). Update the code [version](#Versioning) after merging.

### Commit messages

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    >
    > A paragraph describing what changed and its impact."

Refer to the [7 rules](https://chris.beams.io/posts/git-commit/#seven-rules) on how phrase commit messages.

### Merge Requests

Please make a new GitLab Merge Request with a clear list of what you've done (read more about [merge requests](https://docs.gitlab.com/ee/user/project/merge_requests/)). Assign merge requests to someone else for a code review. Don't approve your own requests. Follow our coding standards (below). Make all of your commits atomic (one feature per commit).

### Versioning

#### Before merging a feature branch

1. Add a new changelog section called `Unreleased` to the top of [CHANGELOG.md](CHANGELOG.md).
2. List the commit messages of all commits that **add features** under sub-section `Added` in the `Unreleased` section. Include the commit messages of all commits that **fix bugs** under sub-section `Fixed` in the `Unreleased` section.
3. Find the commit hash for all listed changes (i.e. using `git log`) and turn commit messages into hyperlinks with the commit hash as destination.

#### After merging a feature branch

1. Calculate a new version number
   * **Minor** bug-fixes and additions increment the **bugfix number**.
   * **Major non-breaking** changes increment the **minor number**.
   * **Major breaking** changes increment the **mayor number**.
2. Create a seperate commit named "Bump version". This commit updates the line `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) to reflect the release date and version: `## [VERSION] - YYYY-MM-DD`
3. Tag the "Bump version" commit with the new version number using `git tag` followed by `git push --tags`.

## Coding standards

General coding standards are:

1. document as you go
2. make your code readable
3. think about security from the start
4. use a standard style guide (such as [PEP 8](https://www.python.org/dev/peps/pep-0008/))
5. use a linter (such as [pylint](https://www.pylint.org/))

An IDE, such as [VS Code](https://code.visualstudio.com/), helps to create and maintain beautiful code.