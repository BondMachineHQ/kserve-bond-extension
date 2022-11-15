package bondartifacts

import (
	"context"
	"fmt"

	bondspec "github.com/BondMachineHQ/kserve-bond-extension/bond-universe/pkg/spec/v1"
	v1 "github.com/opencontainers/image-spec/specs-go/v1"

	"oras.land/oras-go/pkg/content"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {

	// TODO: to put everything in cmd/push + tests
	bondArtifact := bondspec.BondSpec{
		Layers: []bondspec.BondLayer{
			bondspec.BondLayer{
				FPGA: bondspec.BondFPGALayer{
					Model:    "Xilinx XXX",
					Producer: "Xilinx",
				},
				Firmware: []byte("CIAO"),
			},
		},
		Model: bondspec.BondModelLayer{
			BondModelJSON: []byte("{\"CIAO\": \"testmepls\"}"),
			ModelURI:      "example.com/mymode.h5",
		},
	}

	ref := "localhost:5000/oras:test"
	ctx := context.Background()

	// TODO: one layer per firmware with annotations + one layer with model

	// Push file(s) w custom mediatype to registry
	memoryStore := content.NewMemory()

	desc := v1.Descriptor{}
	for _, layer := range bondArtifact.Layers {
		desc, err := memoryStore.Add("xilix-xxxx", bondspec.MediaTypes["Firmware"], layer.Firmware)
		check(err)
		desc.Annotations = map[string]string{}
	}

	desc, err := memoryStore.Add("Model", bondspec.MediaTypes["MLModel"], bondArtifact.Model.BondModelJSON)
	check(err)

	pusher, err := memoryStore.Pusher(ctx, ref)
	check(err)

	result, err := pusher.Push(ctx, desc)
	check(err)
	fmt.Printf("Pushed to %s with digest %s\n", ref, result.Digest())

	// Pull file(s) from registry and save to disk
	// fmt.Printf("Pulling from %s and saving to %s...\n", ref, fileName)
	// fileStore := content.NewFileStore("")
	// defer fileStore.Close()
	// allowedMediaTypes := []string{customMediaType}
	// desc, _, err = oras.Pull(ctx, resolver, ref, fileStore, oras.WithAllowedMediaTypes(allowedMediaTypes))
	// check(err)
	// fmt.Printf("Pulled from %s with digest %s\n", ref, desc.Digest)
	// fmt.Printf("Try running 'cat %s'\n", fileName)
}
