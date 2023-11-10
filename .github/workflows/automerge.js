module.exports = async ({ github, context, dryRun }) => {
  const {
    repo: { owner, repo },
  } = context;

  const MERGE_INTERVAL_MS = 5000; // 5 seconds pause after a merge
  const PR_FETCH_RETRY_INTERVAL_MS = 5000; // 5 seconds between attempts to fetch PR
  const PR_FETCH_MAX_ATTEMPTS = 3; // 3 attempts to fetch PR

  async function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function logRateLimit() {
    const { data: rateLimit } = await github.rest.rateLimit.get();
    console.log(`Rate limit remaining: ${rateLimit.resources.core.remaining}`);
    console.log(
      `Rate limit resets at: ${new Date(rateLimit.resources.core.reset * 1000).toISOString()}`
    );
  }

  async function waitUntilMergeable(prNumber) {
    for (let i = 0; i < PR_FETCH_MAX_ATTEMPTS; i++) {
      const pr = await github.rest.pulls
        .get({
          owner,
          repo,
          pull_number: prNumber,
        })
        .then((res) => res.data);
      console.log(`mergeable: ${pr.mergeable}, mergeable_state: ${pr.mergeable_state}`);

      if (pr.merged) {
        return null;
      }

      if (pr.mergeable === null) {
        console.log(`Waiting for GitHub to recompute mergeability of PR #${prNumber}...`);
        await sleep(PR_FETCH_RETRY_INTERVAL_MS);
        continue;
      }
      return pr.mergeable && pr.mergeable_state === "clean" ? pr : null;
    }
    return null;
  }

  async function allChecksPassed(ref) {
    const checkRuns = await github.paginate(github.rest.checks.listForRef, {
      owner,
      repo,
      ref,
    });

    console.log(`Check runs for ${ref}:`);

    const latestRuns = {};
    for (const run of checkRuns) {
      const { name } = run;
      if (!latestRuns[name] || new Date(run.started_at) > new Date(latestRuns[name].started_at)) {
        latestRuns[name] = run;
      }
    }
    Object.values(latestRuns).forEach(({ name, status, conclusion }) => {
      console.log(`- checkrun: name: ${name}, latest status: ${status}, conclusion: ${conclusion}`);
    });

    return Object.values(latestRuns).every(({ conclusion }) =>
      ["success", "skipped"].includes(conclusion)
    );
  }

  async function allCommitStatusPassed(ref) {
    const commitStatuses = await github.paginate(github.rest.repos.getCombinedStatusForRef, {
      owner,
      repo,
      ref,
    });

    const latestStatuses = {};
    for (const status of commitStatuses) {
      const { context } = status;
      if (
        !latestStatuses[context] ||
        new Date(status.created_at) > new Date(latestStatuses[context].created_at)
      ) {
        latestStatuses[context] = status;
      }
    }

    Object.values(latestStatuses).forEach(({ context, state }) => {
      console.log(`- commit status: context: ${context}, latest state: ${state}`);
    });

    return Object.values(latestStatuses).every(({ state }) => state === "success");
  }

  async function isPrApproved(prNumber) {
    const reviews = await github.paginate(github.rest.pulls.listReviews, {
      owner,
      repo,
      pull_number: prNumber,
    });
    reviews.forEach(({ user, state }) => {
      console.log(`user: ${user.login}, state: ${state}`);
    });
    return reviews.some(({ state }) => state === "APPROVED");
  }

  // List PRs with the "automerge" label updated in the last two weeks
  const twoWeeksAgo = new Date();
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
  const { data: issues } = await github.rest.issues.listForRepo({
    owner,
    repo,
    state: "open",
    sort: "updated",
    direction: "asc",
    per_page: 30,
    labels: "automerge",
    since: twoWeeksAgo.toISOString(),
  });
  // Exclude issues
  const prs = issues.filter((issue) => issue.pull_request);

  if (prs.length === 0) {
    console.log("No PRs to automerge");
    return;
  }

  for (const { number } of prs) {
    console.log(`----- PR #${number} -----`);
    const pr = await waitUntilMergeable(number);
    if (pr === null) {
      console.log(`PR #${number} is not mergeable. Skipping...`);
      continue;
    }

    if (!(await allChecksPassed(pr.head.sha))) {
      console.log(`PR #${pr.number} has failing or pending checks. Skipping...`);
      continue;
    }

    if (!(await allCommitStatusPassed(pr.head.sha))) {
      console.log(`PR #${pr.number} has failing commit statuses. Skipping...`);
      continue;
    }

    if (!(await isPrApproved(pr.number))) {
      console.log(`PR #${pr.number} is not approved. Skipping...`);
      continue;
    }

    try {
      if (dryRun) {
        console.log(`Would merge PR #${pr.number}`);
      } else {
        await github.rest.pulls.merge({
          owner,
          repo,
          pull_number: pr.number,
          merge_method: "squash",
        });
      }
      console.log(`Merged PR #${pr.number}`);
      await sleep(MERGE_INTERVAL_MS);
    } catch (error) {
      console.log(`Failed to merge PR #${pr.number}. Reason: ${error.message}`);
    }
  }

  await logRateLimit();
};
