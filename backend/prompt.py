def format_prompt(profile, jobs):
    job_blocks = "\n\n".join(
        f"Title: {job['title']}\nLink: {job['link']}\nDesc: {job['snippet']}"
        for job in jobs
    )

    return f"""
You are an AI job assistant.

Candidate Profile:
{profile}

Here are some job listings:
{job_blocks}

For each job, rate how well it matches the profile (0–100) and explain why. Only show top 5 matches.
"""
