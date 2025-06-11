const autocannon = require('autocannon');
const { GraphQLClient, gql } = require('graphql-request');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    duration: 30, // Test duration in seconds
    connections: 100, // Number of concurrent connections
    pipelining: 1, // Number of pipelined requests
    timeout: 10, // Timeout in seconds
    endpoint: 'http://localhost:8001/graphql'
};

// GraphQL queries and mutations
const queries = {
    listUsers: gql`
        query {
            listUsers {
                id
                nome
                idade
            }
        }
    `,
    listAllMusic: gql`
        query {
            listAllMusic {
                id
                titulo
                artista
            }
        }
    `,
    listUserPlaylists: gql`
        query($userId: ID!) {
            listUserPlaylists(userId: $userId) {
                id
                nome
                musicas {
                    id
                    titulo
                }
            }
        }
    `,
    listPlaylistMusic: gql`
        query($playlistId: ID!) {
            listPlaylistMusic(playlistId: $playlistId) {
                id
                titulo
                artista
            }
        }
    `
};

const mutations = {
    addUser: gql`
        mutation($nome: String!, $idade: Int!) {
            addUser(nome: $nome, idade: $idade) {
                id
                nome
                idade
            }
        }
    `
};

// Test scenarios
const testScenarios = [
    {
        name: 'Listar Usuários',
        fn: async () => {
            const client = new GraphQLClient(CONFIG.endpoint);
            await client.request(queries.listUsers);
        }
    },
    {
        name: 'Listar Todas as Músicas',
        fn: async () => {
            const client = new GraphQLClient(CONFIG.endpoint);
            await client.request(queries.listAllMusic);
        }
    },
    {
        name: 'Listar Playlists do Usuário',
        fn: async () => {
            const client = new GraphQLClient(CONFIG.endpoint);
            await client.request(queries.listUserPlaylists, { userId: '1' });
        }
    },
    {
        name: 'Listar Músicas da Playlist',
        fn: async () => {
            const client = new GraphQLClient(CONFIG.endpoint);
            await client.request(queries.listPlaylistMusic, { playlistId: '1' });
        }
    }
];

// Generate HTML report
function generateHTMLReport(results) {
    const html = `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Testes de Carga - Serviço GraphQL</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .chart-container {
                margin: 20px 0;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1, h2 {
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f8f9fa;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relatório de Testes de Carga - Serviço GraphQL</h1>
            <h2>Configuração dos Testes</h2>
            <table>
                <tr>
                    <th>Parâmetro</th>
                    <th>Valor</th>
                </tr>
                <tr>
                    <td>Duração</td>
                    <td>${CONFIG.duration} segundos</td>
                </tr>
                <tr>
                    <td>Conexões Concorrentes</td>
                    <td>${CONFIG.connections}</td>
                </tr>
                <tr>
                    <td>Pipelining</td>
                    <td>${CONFIG.pipelining}</td>
                </tr>
                <tr>
                    <td>Timeout</td>
                    <td>${CONFIG.timeout} segundos</td>
                </tr>
            </table>

            <div class="chart-container">
                <canvas id="requestsChart"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="responseTimeChart"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="successRateChart"></canvas>
            </div>

            <h2>Resultados Detalhados</h2>
            <table>
                <tr>
                    <th>Cenário</th>
                    <th>Total de Requisições</th>
                    <th>Erros</th>
                    <th>Taxa de Sucesso</th>
                    <th>Tempo Médio de Resposta</th>
                    <th>Requisições por Segundo</th>
                </tr>
                ${results.map(r => `
                    <tr>
                        <td>${r.name}</td>
                        <td>${r.requestCount}</td>
                        <td>${r.errorCount}</td>
                        <td>${r.successRate.toFixed(2)}%</td>
                        <td>${r.avgResponseTime.toFixed(2)}ms</td>
                        <td>${r.rps.toFixed(2)}</td>
                    </tr>
                `).join('')}
            </table>
        </div>

        <script>
            const results = ${JSON.stringify(results)};
            
            // Gráfico de Requisições
            new Chart(document.getElementById('requestsChart'), {
                type: 'bar',
                data: {
                    labels: results.map(r => r.name),
                    datasets: [{
                        label: 'Total de Requisições',
                        data: results.map(r => r.requestCount),
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Total de Requisições por Cenário'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Gráfico de Tempo de Resposta
            new Chart(document.getElementById('responseTimeChart'), {
                type: 'bar',
                data: {
                    labels: results.map(r => r.name),
                    datasets: [{
                        label: 'Tempo Médio de Resposta (ms)',
                        data: results.map(r => r.avgResponseTime),
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Tempo Médio de Resposta por Cenário'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Gráfico de Taxa de Sucesso
            new Chart(document.getElementById('successRateChart'), {
                type: 'bar',
                data: {
                    labels: results.map(r => r.name),
                    datasets: [{
                        label: 'Taxa de Sucesso (%)',
                        data: results.map(r => r.successRate),
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Taxa de Sucesso por Cenário'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    `;

    fs.writeFileSync(path.join(__dirname, 'relatorio_teste_carga_graphql.html'), html);
}

async function runLoadTest(scenario) {
    const instance = autocannon({
        url: CONFIG.endpoint,
        connections: CONFIG.connections,
        pipelining: CONFIG.pipelining,
        duration: CONFIG.duration,
        timeout: CONFIG.timeout,
        setupRequest: async (req) => {
            req.body = JSON.stringify({
                query: scenario.fn.toString()
            });
            req.headers['content-type'] = 'application/json';
        }
    });

    return new Promise((resolve) => {
        autocannon.track(instance, { renderProgressBar: false });
        instance.on('done', (results) => {
            resolve({
                name: scenario.name,
                requestCount: results.requests.total,
                errorCount: results.errors,
                successRate: ((results.requests.total - results.errors) / results.requests.total) * 100,
                avgResponseTime: results.latency.average,
                rps: results.requests.average
            });
        });
    });
}

async function runAllLoadTests() {
    console.log('🚀 Iniciando testes de carga do serviço GraphQL...');
    const results = await Promise.all(testScenarios.map(runLoadTest));
    generateHTMLReport(results);
    console.log('✅ Testes de carga concluídos. Relatório gerado: relatorio_teste_carga_graphql.html');
}

// Run all load tests
runAllLoadTests(); 