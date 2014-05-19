ide = getImageID(); //remnant of a forgone era

//main: collect image info, save metadata
//loop 1x

Dialog.create("Number of segments");
Dialog.addNumber("How many segments are visible?", 3);
Dialog.show(); //get input from user: number of segments
number = Dialog.getNumber();
dir = getDirectory("home") + "Desktop/temp/";
name = getTitle();
print("\\Clear") //clears log window
print("img_title " + name);
print("no_segments " + number);
selectWindow("Log");
saveAs("Text", "" + dir + "/" + name + "_meta.txt");

//prep: set parameters linewidth and color; clear previous measurements
//loop 1x
run("Line Width...", "line=2");
run("Colors...", "foreground=red background=white selection=yellow");
run("Clear Results");

//measure:
//loop 3x
for (b=0; b<3; b++) {
	query = "Draw a line:";
	measure_length();
	saveAs("Measurements", "" + dir + "/" + name + b+1 + "_len.txt");
	run("Clear Results");

	query = "Draw area:";
	measure_area();
	saveAs("Measurements", "" + dir + "/" + name + b+1 + "_area.txt");
	run("Clear Results");

selectImage(name);
close();
open(name);
}

//final: close image
selectImage(name);
close();

//functions: measure length and measure area
//no loop
function measure_length() {
	setTool("polyline");
	string = query;
	waitForUser(string);
	run("Measure");
	updateResults;
	run("Draw");
}

function measure_area() {
	//run("Clear Results");
	setTool("polygon");
	string = query;
	waitForUser(string);
	run("Measure");
	updateResults;
	run("Draw");
}