module.exports = async ({ context, github }) => {
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  const { sha: ref } = context;
  const { owner, repo } = context.repo;
  const { number: issue_number } = context.issue;
  console.log(context);
  console.log(ref, owner, repo);

  await sleep(10000);
  const resp = await github.checks.listForRef({
    owner,
    repo,
    ref,
    app_id: 1861, // ID of the DCO check app
  });
  const dcoCheck = resp.data.check_runs[0];
  const { html_url, conclusion } = dcoCheck;

  if (conclusion !== "success") {
    const body = `The DCO check failed. Please sign off your commits:\n${html_url}`;
    await github.issues.createComment({
      owner,
      repo,
      issue_number,
      body,
    });
  }
};
