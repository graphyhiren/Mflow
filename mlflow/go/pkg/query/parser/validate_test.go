package parser_test

import (
	"testing"

	"github.com/mlflow/mlflow/mlflow/go/pkg/query"
)

func TestValidQueries(t *testing.T) {
	samples := []string{
		"metrics.foobar = 40",
		"metrics.foobar = 40 AND run_name = \"bouncy-boar-498\"",
		"tags.\"mlflow.source.name\" = \"scratch.py\"",
		"metrics.accuracy > 0.9",
		"params.\"random_state\" = \"8888\"",
		"params.`random_state` = \"8888\"",
		"params.solver ILIKE \"L%\"",
		"params.solver LIKE \"l%\"",
		"datasets.digest IN ('77a19fc0')",
	}

	for _, sample := range samples {
		t.Run(sample, func(t *testing.T) {
			_, err := query.ParseFilter(sample)
			if err != nil {
				t.Errorf("unexpected parse error: %v", err)
			}
		})
	}
}
