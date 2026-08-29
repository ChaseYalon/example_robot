Please note this is a draft written as a proposal, and is NOT approved or endorsed by FRC 5113. The current official version can be found [here](https://github.com/FRC5113/2027-Pterodactyl-Rewrite/blob/main/Philosophy.md)

# Philosophy and Standards of 5113's Robot Code

## General Guidelines
Code is "correct" if...
1. All control paths are tested (if a path is not worth testing, think about if it should be included considering point 3) AND
2. The Black formatter has been applied AND
3. All redundant, unused, unreachable, or otherwise legacy code has been removed AND
4. There are no excessive comments AND
5. It implements the PRE-AGREED UPON interface for the code AND
6. It follows the style guidelines bellow
A note on point 5: during competition season, it is often the case that multiple components are being developed at the same time, in that case it would be frustrating for the author of component A to expect component B to have a certain method, only to find out it has not.

### "All Control Paths" are tested if...
Note: This entire requirement may be waived by majority vote of the software team, within 3 weeks of any competition.
Note: If there is a given execution path where it is impossible independently execute (say a deeply nested if statement), than consider that test unnecessary.
1. Every possible execution path (so every if, else, and elif branch) has at least 1 unit test ensuring it performs its intended function AND
2. For every pair of interacting control paths (meaning the outcome of one changes the behavior of the other; for example, one sets a variable that the other reads, or both write to the same motor), there is at least 1 test exercising that pair together AND
3. Every loop is tested three times (if the loop does not iterate at all, iterates once, and iterates $N$ times where $N \in \mathbb{N}_{>1}$ times) AND
4. If a section of code can raise an exception, that code is tested for the case with and without the exception UNLESS the exception being raised means the robot should be Emergency Stopped, in which case testing is unnecessary

### "The Black formatter has been applied" if...
1. All code has been successfully formatted by Black, in compliance with its standards

### "All redundant, unused, unreachable, or otherwise legacy code has been removed" if...
1. Every function, class, and variable defined in the code has at least one call site, reference, or read, found either in the code itself, or named explicitly by the reviewer as a framework callback (eg. `teleopPeriodic`) or hardware-consumed config value (eg. `neutral_mode`) AND
2. Every branch of every if/elif/else has a path by which it could be reached, given the possible values of its condition AND
3. No code exists after an unconditional `return`, `raise`, `break`, or `continue` within the same block

### "There are no excessive comments" if...
Note: This section does not apply to triple quoted (""") Doc Comments, see the rules regarding point 5 for those guidelines
1. There is no case where, the information provided by a comment could instead be conveyed with a better variable/function name AND
2. There are no comments to explain WHAT code does (if the code is not self evident, rewrite it) AND
3. No comment addresses more than one "why" at a time — a comment explaining several unrelated reasons should be split into separate comments placed next to what they each explain

### "The pre-agreed interface is implemented" if...
1. The interface (including the name, parameters, with types and units, where units apply, and return type) was issued in writing (eg. email, issue, Google Doc) before implementation of the component began AND
2. Any change made to the interface after implementation began was also issued in writing, before the change was implemented, by whoever discovered the original interface no longer worked AND
3. Every function's name, parameters, and return type are IDENTICAL to the most recent written version of the interface AND
4. The functionality of an externally exposed function matches what its name and the written interface imply it should do (ie a function named `add` should not return the product of its two parameters)

### "A code follows the style guidelines bellow" if...
Note: This is on top of black, not instead of black
1. Constants are named in all caps, written in UPPER_SNAKE_CASE AND
2. Class names are written in PascalCase, AND
3. Variable, function, and method names are written in snake_case, AND
4. The function of a variable is inferable from its name (ie: "count" is ok, "thing" is not), AND
5. All functions, fields, and variables are either explicitly annotated with or be obvious enough that Pyright can infer the type, AND
6. Nesting is not deeper than 4 levels, without a comment explaining why it is impossible to have less, AND
7. Units belong in the type, not the name — eg. `time: nanoseconds` is correct, `time_ns: float` is not, since a type-based unit can be checked by Pyright and a name-based one cannot
8. Any other PURELY FORMATTING/AESTHETIC condition set out by the software lead, that do not conduct any points in this doc, and announced publicly in either the Discord or the GitHub are followed.

## GitHub Guidelines
1. All code should be done on a branch of the main repo, named with the programmer's initials and the component being worked on, all in caps, separated by an underscore. Example: if John Doe is working on the intake, the branch should be "JD_INTAKE". If two programmers' initials conflict, whoever joined the team first uses initials; anyone who joined later uses their first name and last initial instead. Example: if Jane Doe joined after John Doe and also needs the initials "JD", she should use "JANE-D_ROBOT" instead.
2. When making a commit, it should be structured as [COMPONENT1_WORKED_ON, COMPONENT2_WORKED_ON...](issue-number_1, issue-number_2...) BRIEF_DESCRIPTION. If no issue is associated with the change, omit the parentheses entirely. Example: fixing issue 323, where the intake would not raise: "[Intake](323) Made it so intake would raise." Example with no associated issue: "[ShooterController, Odometry] Added Shoot-On-The-Move Solver."
## PR Review Procedures
1. Every PR needs at least 2 reviewers (only 1 is required within 3 weeks of a competition). Reviewers must have been to at least one competition. Nobody merges code directly into main without review — the only exception is if the software lead decides the situation is urgent enough, and this can only happen during a competition itself.
2. To review a PR, you must not have written any of the code in it. The first two people to volunteer become the reviewers. If nobody volunteers, the software lead can assign reviewers instead.
3. Code that isn't "correct" (see General Guidelines) can never be merged. No vote, discussion, or exception changes this — it's a hard rule.
4. Even if code is "correct," reviewers can still reject it for other reasons (eg. it doesn't fit well with other code, it's the wrong time to add it, etc). If either reviewer says no, the PR does not merge — it doesn't need both reviewers to agree on the rejection.
5. If someone thinks a rejected PR was rejected unfairly, they can appeal to the whole software team.
6. When an appeal happens, anyone on the team can speak about the code. Then everyone votes "merge" or "no merge" — people not physically present can vote in the software Discord channel. Whichever option gets more votes wins, and a tie means no merge. This vote can turn a "no merge" into a "merge." 
7. Instead of rejecting a PR outright, a reviewer can ask for changes and give a deadline for them. A reviewer can do this as many times as they want — there's no limit on how many rounds of changes can be requested. If the author doesn't make the changes well enough, the reviewer can reject the PR. If the author refuses to make further changes, they can force a vote (see point 5) instead of continuing the cycle.
8. If a reviewer doesn't respond with a decision within 3 business days (Monday–Friday, plus Saturday if the team practiced that day), the software lead can replace them with a different reviewer.

Note: "correct" code is the BARE MINIMUM, "incorrect" code should never me merged, however just because code is "correct" does not mean it is optimal, or even acceptable. For example you could name a variable "wtf_is_this_hit_me_hit_me" and be "correct", however that should not be merged


## Changing this Document
This document once committed and approved by a majority of software AND the advisors, may only be changed by 2/3 of software and the advisors during the year. It may be changed by only 1/2 software and the advisors, withing 2 weeks of the year starting.