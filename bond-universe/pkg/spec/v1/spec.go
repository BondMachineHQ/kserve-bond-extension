package spec

// FPGA json description layer
type BondFPGALayer struct {
	Model    string
	Producer string
}

// ML model description layer
type BondModelLayer struct {
	BondModelJSON []byte
	ModelURI      string
}

// Bond firmware description layer
type BondLayer struct {
	FPGA     BondFPGALayer
	Firmware []byte
}

// BondSpec artifact manifest type
type BondSpec struct {
	Layers []BondLayer
	Model  BondModelLayer
}

// MediaTypes are the whole set of types of layer that can be provided
var MediaTypes = map[string]string{
	"FPGAModel": "bond.fpga.model",
	"Producer":  "bond.fpga.producer",
	"Firmware":  "bond.fpga.firmware",
	"MLModel":   "bond.model+json",
}
