# mingpao_edu_jobs
A helpful python script to crawl all education jobs posted on mingpao website into a single html file.

![ScreenShot](screenshot/screen1.png)


# Usage
Crawl and generate a new daily html every hour
```sh
python crawl.py
```

# Output
```
static/index.html -> static/<yyyymmdd>.html
```

Start a web server on port 8080 to serve *static/index.html*
```sh
python app.py
```


# Why to make it?
Jobs posted on mingpao website show a job in two levels. Frist is a list view showing job title, second is the job details which you can see after clicking into a link. This is not convenient for job seeker to browse.

