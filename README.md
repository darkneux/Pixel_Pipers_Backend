<h1>Pixel Pipers Backend</h1>

<p>This repository contains the backend code for the Pixel Pipers application.</p>

<h2>Setup</h2>

<h3>Clone the repository:</h3>

<pre><code>git clone https://github.com/darkneux/Pixel_Pipers_Backend.git
</code></pre>


<h3>Create a <code>credentials.json</code> file in the root directory of the project with the following structure:</h3>

<pre><code>{
  "username": "&lt;your_username&gt;",
  "password": "&lt;your_password&gt;",
  "token": "&lt;create_a_token&gt;"
}
</code></pre>

<p>Replace <code>&lt;your_username&gt;</code> and <code>&lt;your_password&gt;</code> with your desired username and password.<br>
Generate a token with 12 characters and replace <code>&lt;create_a_token&gt;</code>.</p>

<h3>Cloudinary Credentials:</h3>

<p>To enable image uploading functionality, you'll need to add your Cloudinary credentials to <code>app.py</code>. Follow these steps:</p>

<ol>
<li>Obtain your Cloudinary API credentials (API Key, API Secret, Cloud Name).</li>
<li>Open <code>app.py</code>.</li>
<li>Find the section where Cloudinary configuration is set up (typically near the top of the file).</li>
<li>Replace the placeholders with your actual Cloudinary credentials:</li>
</ol>

<pre><code>cloudinary.config( 
  cloud_name = "&lt;your_cloud_name&gt;", 
  api_key = "&lt;your_api_key&gt;", 
  api_secret = "&lt;your_api_secret&gt;"
)
</code></pre>

<h3>Run the application:</h3>

<pre><code>python app.py
</code></pre>

<h2>Docker Setup</h2>

<p>Alternatively, you can run the application using Docker.</p>

<h3>Build Docker Image:</h3>

<p>Build the Docker image by running the following command from the root directory of the project:</p>

<pre><code>sudo docker build -t &lt;image_name&gt; .
</code></pre>

<p>Replace <code>&lt;image_name&gt;</code> with your desired name for the Docker image.</p>

<h3>Run Docker Container:</h3>

<p>Once the Docker image is built, you can run the application within a Docker container using the following command:</p>

<pre><code>sudo docker run -p 80:5000 -v ./PIPE_model:/code/ &lt;image_name&gt;
</code></pre>

<ul>
<li><code>-p 80:5000</code> maps port 80 of the host machine to port 5000 of the Docker container, allowing access to the application.</li>
<li><code>-v ./PIPE_model:/code/</code> mounts the <code>PIPE_model</code> directory from the host machine to <code>/code/</code> within the container, ensuring that the application can access the required files.</li>
</ul>
