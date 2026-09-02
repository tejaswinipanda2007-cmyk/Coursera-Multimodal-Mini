"""
Sample raw assets — simulates what would come from Coursera's real content.

In production, these would be:
- video   -> actual video file + auto-generated transcript (via Whisper API etc.)
- slide   -> PDF/PPT parsed via OCR
- quiz    -> question bank from LMS database
- discussion -> forum posts from students

For our 1-month solo build, we hand-write realistic sample data.
This is a normal, honest thing to do for a course capstone -
document it clearly in your README as "simulated data" so it's transparent.
"""

RAW_ASSETS = [
    {
        "source_id": "video_001",
        "modality": "video",
        "source_title": "Lecture 3: Gradient Descent",
        "topic": "Gradient Descent",
        # (timestamp, text) pairs simulating a transcript with timestamps
        "content": [
            ("00:00:10", "Today we'll learn gradient descent, an optimization algorithm."),
            ("00:02:45", "The learning rate controls how big each step is during optimization."),
            ("00:05:30", "If the learning rate is too high, the algorithm can overshoot the minimum and diverge."),
            ("00:08:15", "A common mistake students make is confusing learning rate with the number of epochs."),
            ("00:11:00", "Let's look at an example with a simple quadratic loss function."),
        ],
    },
    {
        "source_id": "slide_001",
        "modality": "slide",
        "source_title": "Slide Deck: Optimization Basics",
        "topic": "Gradient Descent",
        "content": [
            (None, "Slide 4: Learning Rate. Formula: theta = theta - alpha * gradient."),
            (None, "Slide 5: Too high alpha causes divergence. Too low alpha causes slow convergence."),
            (None, "Slide 6: Epochs = number of passes over the full training dataset."),
        ],
    },
    {
        "source_id": "quiz_001",
        "modality": "quiz",
        "source_title": "Quiz: Optimization Concepts",
        "topic": "Gradient Descent",
        "content": [
            (None, "Question: What happens if the learning rate is too large? "
                    "40% of learners answered incorrectly, most confusing it with epoch count."),
            (None, "Question: Define one epoch in gradient descent. "
                    "35% of learners incorrectly said it means one gradient update step."),
        ],
    },
    {
        "source_id": "discussion_001",
        "modality": "discussion",
        "source_title": "Forum: Week 2 Discussion",
        "topic": "Gradient Descent",
        "content": [
            (None, "Student post: I'm confused, is learning rate the same as epochs? "
                    "The lecture didn't make it clear at 8 minutes in."),
            (None, "Student post: My loss keeps increasing every step, is my learning rate too high?"),
        ],
    },
]
