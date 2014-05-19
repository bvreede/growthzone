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
	if (number>0) {
	query = "1: Draw a line from the tip of the growthzone to the first stripe:";
	measure_length();
	}
	query = "2: Draw a line measuring the width of the growthzone at its widest part:";
	measure_length();
	if (number>0) {
	query = "3: Draw a line along the first stripe:";
	measure_length();
	}
	if (number>1) {
	query = "4: Draw a line along the second stripe:";
	measure_length();
	}
	if (number>2) {
	query = "5: Draw a line along the third stripe:";
	measure_length();
	}
	if (number>1) {
	query = "6: Draw a line between the first and second stripe:";
	measure_length();
	}
	if (number>2) {
	query = "7: Draw a line between the second and third stripe:";
	measure_length();
	}

	saveAs("Measurements", "" + dir + "/" + name + b+1 + "_len.txt");
	run("Clear Results");

	if (number>0) {
	query = "8: Draw the area of the growthzone up to the first stripe:";
	measure_area();
	}
	if (number>1) {
	query = "9: Draw the area of the growthzone up to the second stripe:";
	measure_area();
	}
	if (number>2) {
	query = "10: Draw the area of the growthzone up to the third stripe:";
	measure_area();
	}
	
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
	setTool("line");
	waitForUser(query);
	run("Measure");
	updateResults;
	run("Draw");
}

function measure_area() {
	//run("Clear Results");
	setTool("polygon");
	waitForUser(query);
	run("Measure");
	updateResults;
	run("Draw");
}